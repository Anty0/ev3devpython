import logging
import math
import time

from ev3dev.auto import Motor

from utils.calc.regulator import ValueRegulator
from utils.coordinator import Action, CycleThreadCoordinator
from utils.hardware.wheel import Wheel
from utils.utils import crop_r

log = logging.getLogger(__name__)

_REG_SPEED_P = 1
_REG_SPEED_I = 0.1
_REG_SPEED_D = 2

# _REG_ERROR_P = 0.3
# _REG_ERROR_I = 0.1
# _REG_ERROR_D = 0.4

_CYCLE_TIME = 0.05


class MotorAction(Action):
    def __init__(self, wheel, speed, max_duty_cycle=100):
        self.wheel = wheel
        self._motor = wheel.motor
        self._speed = speed
        self._max_duty_cycle = crop_r(max_duty_cycle, 100)

        self._elapsed_time = time.time()
        self._start_position = self._motor.position
        self._speed_regulator = ValueRegulator(const_p=_REG_SPEED_P, const_i=_REG_SPEED_I, const_d=_REG_SPEED_D,
                                               getter_target=self.target_tacho_counts)
        # self._error_regulator = ValueRegulator(const_p=_REG_ERROR_P, const_i=_REG_ERROR_I,
        #                                        const_d=_REG_ERROR_D, const_target=0)

    def actual_progress(self):
        return (self.traveled_tacho_counts() / self._speed) if self._speed != 0 else None

    def traveled_tacho_counts(self):
        return self._motor.position - self._start_position

    def traveled_units(self):
        return self.traveled_tacho_counts() / self.wheel.unit_ratio / self.wheel.total_ratio

    def target_tacho_counts(self):
        return self._speed * self._elapsed_time + self._start_position

    def target_units(self):
        return self.target_tacho_counts() / self.wheel.unit_ratio / self.wheel.total_ratio

    def on_start(self):
        self._speed_regulator.reset()
        # self._error_regulator.reset()

        self._start_position = self._motor.position
        self._motor.run_direct(duty_cycle_sp=0)

    def handle_loop(self, elapsed_time, progress_error):
        # if progress_error == 0:
        #     error = 0
        # else:
        #     error = (progress_error * progress_error / 2) * (progress_error / abs(progress_error))
        #     if abs(error) < 0.1:
        #         error = 0
        #     else:
        #         error -= 0.1 * (error / abs(error))
        self._elapsed_time = elapsed_time  # + error
        # duty_cycle = utils.crop_r(self._speed_regulator.regulate(self._motor.position), self._max_duty_cycle)
        # duty_cycle += self._error_regulator.regulate(-progress_error * self.speed)
        # self._motor.duty_cycle_sp = utils.crop_r(duty_cycle, self._max_duty_cycle)

        self._motor.duty_cycle_sp = crop_r(self._speed_regulator.regulate(self._motor.position),
                                           self._max_duty_cycle)

    def on_stop(self):
        self._motor.stop()


class DriveCoordinator(CycleThreadCoordinator):
    def __init__(self, motor_actions, time_len=None, angle_deg=None, distance_unit=None):
        CycleThreadCoordinator.__init__(self, motor_actions, cycle_time=_CYCLE_TIME)
        self.setDaemon(True)

        self._time_len = time_len
        self._angle_deg = angle_deg
        self._distance_unit = distance_unit

        if len(motor_actions) == 0:
            self.stop()
        else:
            self._min_action = min(motor_actions, key=lambda motor_action: motor_action.wheel.offset)
            self._max_action = max(motor_actions, key=lambda motor_action: motor_action.wheel.offset)

    def _is_stop_loop(self):
        return CycleThreadCoordinator._is_stop_loop(self) \
               or self._check_time() \
               or self._check_distance() \
               or self._check_angle()

    def _check_time(self) -> bool:
        return self._time_len is not None and time.time() - self._start_time >= self._time_len

    def _check_distance(self) -> bool:
        if self._distance_unit is None or self._min_action.wheel.offset == self._max_action.wheel.offset:
            return False

        if self._distance_unit == 0:
            return True

        min_action = self._min_action
        max_action = self._max_action
        min_traveled = min_action.traveled_units()
        max_traveled = max_action.traveled_units()

        traveled_delta_per_offset_delta = max_traveled - min_traveled / max_action.wheel.offset - min_action.wheel.offset
        distance_unit = max_traveled - (max_action.wheel.offset * traveled_delta_per_offset_delta)

        return abs(distance_unit) > abs(self._distance_unit)

    def _check_angle(self) -> bool:
        if self._angle_deg is None or self._min_action.wheel.offset == self._max_action.wheel.offset:
            return False

        if self._angle_deg == 0:
            return True

        min_action = self._min_action
        max_action = self._max_action
        min_traveled = min_action.traveled_units()
        max_traveled = max_action.traveled_units()

        if min_traveled == max_traveled or abs(max_traveled) + abs(min_traveled) < 0.5:
            return False

        if max_traveled == 0:
            min_radius = min_action.wheel.offset - max_action.wheel.offset
            max_radius = 0
        elif min_traveled == 0:
            min_radius = 0
            max_radius = max_action.wheel.offset - min_action.wheel.offset
        else:
            ratio = min_traveled / max_traveled
            radius = (min_action.wheel.offset - ratio * max_action.wheel.offset) / (ratio - 1)
            min_radius = radius + min_action.wheel.offset
            max_radius = radius + max_action.wheel.offset

        if abs(min_radius) > abs(max_radius):
            circuit = 2 * min_radius * math.pi
            angle_deg = (min_traveled / circuit) * 360
        else:
            circuit = 2 * max_radius * math.pi
            angle_deg = (max_traveled / circuit) * 360

        return abs(angle_deg) > abs(self._angle_deg)


class Pilot:
    def __init__(self, *wheels: Wheel):
        self._running_coordinator = None
        self._wheels = []
        self._has_wheels = False

        self._max_speed_tacho = 0
        self._max_speed_deg = 0
        self._max_speed_unit = 0

        self._min_wheel = 0
        self._max_wheel = 0

        self._max_offset = 0

        self.wheels = wheels

    @property
    def is_connected(self):
        return self._has_wheels

    @property
    def wheels(self) -> list:
        return self._wheels

    @wheels.setter
    def wheels(self, wheels: list):
        self.stop()
        self.wait_to_stop()

        self._wheels = wheels

        if len(self._wheels) == 0:
            self._has_wheels = False
            self._min_wheel = None
            self._max_wheel = None
        else:
            self._has_wheels = all((wheel.motor.connected for wheel in self._wheels))

            self._min_wheel = min(range(len(self._wheels)), key=lambda i: self._wheels[i].offset)
            self._max_wheel = max(range(len(self._wheels)), key=lambda i: self._wheels[i].offset)

        self._refresh_max_speed()
        self._refresh_max_offset()
        self.reset()

    def get_max_speed_tacho(self):
        return self._max_speed_tacho

    def get_max_speed_deg(self):
        return self._max_speed_deg

    def get_max_speed_unit(self):
        return self._max_speed_unit

    def _refresh_max_speed(self):
        if not self._has_wheels or len(self._wheels) == 0:
            self._max_speed_tacho = 0
            self._max_speed_deg = 0
            self._max_speed_unit = 0
        else:
            self._max_speed_tacho = self._wheels[0].motor.max_speed
            self._max_speed_deg = self._max_speed_tacho / self._wheels[0].total_ratio
            self._max_speed_unit = self._max_speed_deg / self._wheels[0].unit_ratio
            for wheel in self._wheels:
                max_speed_tacho = wheel.motor.max_speed
                self._max_speed_tacho = min(abs(max_speed_tacho), self._max_speed_tacho)
                max_speed_deg = max_speed_tacho / wheel.total_ratio
                self._max_speed_deg = min(abs(max_speed_deg), self._max_speed_deg)
                max_speed_unit = max_speed_deg / wheel.unit_ratio
                self._max_speed_unit = min(abs(max_speed_unit), self._max_speed_unit)

    def _refresh_max_offset(self):
        if len(self._wheels) == 0:
            self._max_offset = 0
        else:
            self._max_offset = abs(self._wheels[0].offset)
            for wheel in self._wheels:
                self._max_offset = max(self._max_offset, abs(wheel.offset))

    def _stop_coordinator(self):
        if self._running_coordinator is not None:
            self._running_coordinator.stop()
            if self._running_coordinator.is_alive():
                self._running_coordinator.join()
            self._running_coordinator = None

    def reset(self):
        self._stop_coordinator()
        if self._has_wheels:
            for wheel in self._wheels:
                wheel.motor.reset()
                wheel.motor.stop_action = 'brake'

    def stop(self):
        self._stop_coordinator()
        for wheel in self._wheels:
            wheel.motor.stop()

    def _course_percent_to_speeds(self, course_percent: float, max_speed: float, min_speed: float = 0,
                                  target_speed: float = None, mul_speed: float = 1):
        min_speed = abs(min_speed)
        max_speed = abs(max_speed)
        mul_speed = crop_r(mul_speed, 1)

        if max_speed == 0 or mul_speed == 0 or min_speed > max_speed:
            return [0] * len(self._wheels)

        if target_speed is None:
            target_speed = max_speed
        else:
            target_speed_abs = abs(target_speed)
            if target_speed_abs > max_speed:
                target_speed = max_speed * (target_speed / target_speed_abs)

        if course_percent == 0:
            return [target_speed * mul_speed] * len(self._wheels)

        if target_speed != 0 and min_speed == max_speed:
            speed = min_speed * (abs(target_speed) / target_speed)
            return [speed] * len(self._wheels)

        speeds = []

        # max_pos = self._max_offset * (-1 if course_percent > 0 else 1)
        # for wheel in self._wheels:
        #     effect = abs(wheel.offset - max_pos) / (2 * self._max_offset)
        #     speeds.append(max_speed - (abs(course_percent) * effect / 100 * max_speed))

        half_course = course_percent / 100 * max_speed / 2

        max_gen_speed = -max_speed
        min_gen_speed = max_speed
        for wheel in self._wheels:
            effect = -wheel.offset / self._max_offset
            speed = target_speed + (half_course * effect)
            max_gen_speed = max(max_gen_speed, speed)
            min_gen_speed = min(min_gen_speed, speed)
            speeds.append(speed)

        diff = 0
        if max_gen_speed > max_speed:
            diff = max_gen_speed - max_speed
        if min_gen_speed < -max_speed:
            diff_tmp = min_gen_speed + max_speed
            if diff == 0 or abs(diff) < abs(diff_tmp):
                diff = diff_tmp

        if diff != 0:
            if max_gen_speed - diff > max_speed or min_gen_speed - diff < -max_speed:
                target_mul = max_speed / (max_speed + abs(diff))
                speeds = [speed * target_mul for speed in speeds]
            else:
                speeds = [speed - diff for speed in speeds]

        if mul_speed != 1:
            speeds = [speed * mul_speed for speed in speeds]

        if min_speed != 0:
            max_found_speed = max((abs(speed) for speed in speeds))
            if max_found_speed < min_speed:
                target_mul = min_speed / max_found_speed
                speeds = [speed * target_mul for speed in speeds]

        return speeds

    def _course_r_to_speeds(self, course_r, speed, max_speed):
        if course_r is 0:
            course_r = 0.0001
        no_warn = False
        if speed is None:
            speed = max_speed
            no_warn = True

        speeds = []
        max_found_speed = 0
        if course_r is None:
            max_found_speed = speed
            for i in range(len(self._wheels)):
                speeds.append(speed)
        else:
            center_way_circuit = 2 * -course_r * math.pi
            one_unit_speed = speed / center_way_circuit
            for i in range(len(self._wheels)):
                wheel = self._wheels[i]
                wheel_way_circuit = 2 * (-course_r + wheel.offset) * math.pi
                wheel_speed_unit = one_unit_speed * wheel_way_circuit
                max_found_speed = max(max_found_speed, abs(wheel_speed_unit))
                speeds.append(wheel_speed_unit)

        if max_found_speed > max_speed:
            if not no_warn:
                log.warning('Can\'t use drive speed ' + str(speed) + ', '
                            + 'it requires wheel speed ' + str(max_found_speed) + ', '
                            + 'but wheel max wheel speed is ' + str(max_speed) + '. '
                            + 'Drive will be slower.')
            change = self._max_speed_unit / max_found_speed
            for i in range(len(speeds)):
                speeds[i] *= change
            max_found_speed *= change
        return speeds

    def _generate_max_speeds_tacho(self):
        speeds_tacho = []
        for i in range(len(self._wheels)):
            speeds_tacho.append(self._max_speed_tacho)
        return speeds_tacho

    def _generate_max_speeds_deg(self):
        speeds_deg = []
        for i in range(len(self._wheels)):
            speeds_deg.append(self._max_speed_deg)
        return speeds_deg

    def _generate_max_speeds_unit(self):
        speeds_unit = []
        for i in range(len(self._wheels)):
            speeds_unit.append(self._max_speed_unit)
        return speeds_unit

    def _validate_len(self, data_array):
        if len(data_array) != len(self._wheels):
            raise Exception('len(data_array) != len(wheels)')

    def _speeds_unit_to_deg(self, speeds_unit):
        speeds_deg = []
        for i in range(len(speeds_unit)):
            speeds_deg.append(speeds_unit[i] * self._wheels[i].unit_ratio)
        return speeds_deg

    def _speeds_deg_to_tacho(self, speeds_deg):
        speeds_tacho = []
        for i in range(len(speeds_deg)):
            speeds_tacho.append(speeds_deg[i] * self._wheels[i].total_ratio)
        return speeds_tacho

    def _raw_run_unit(self, time_len=None, angle_deg=None, distance_unit=None, speeds_unit=None, max_duty_cycle=100,
                      async=False):
        if speeds_unit is None:
            speeds_tacho = self._generate_max_speeds_tacho()
        else:
            self._validate_len(speeds_unit)
            speeds_tacho = self._speeds_deg_to_tacho(self._speeds_unit_to_deg(speeds_unit))

        self._raw_run_tacho_ready(time_len, angle_deg, distance_unit, speeds_tacho, max_duty_cycle, async)

    def _raw_run_deg(self, time_len=None, angle_deg=None, distance_unit=None, speeds_deg=None, max_duty_cycle=100,
                     async=False):
        if speeds_deg is None:
            speeds_tacho = self._generate_max_speeds_tacho()
        else:
            self._validate_len(speeds_deg)
            speeds_tacho = self._speeds_deg_to_tacho(speeds_deg)

        self._raw_run_tacho_ready(time_len, angle_deg, distance_unit, speeds_tacho, max_duty_cycle, async)

    def _raw_run_tacho(self, time_len=None, angle_deg=None, distance_unit=None,
                       speeds_tacho=None, max_duty_cycle=100, async=False):
        if speeds_tacho is None:
            speeds_tacho = self._generate_max_speeds_tacho()
        else:
            self._validate_len(speeds_tacho)

        self._raw_run_tacho_ready(time_len, angle_deg, distance_unit, speeds_tacho, max_duty_cycle, async)

    def _raw_run_tacho_ready(self, time_len, angle_deg, distance_unit, speeds_tacho, max_duty_cycle, async):
        # async = True  # TODO: test
        if async:
            self._stop_coordinator()
            if time_len is not None:
                for i in range(len(speeds_tacho)):
                    self._wheels[i].motor.run_timed(speed_sp=speeds_tacho[i], time_sp=int(time_len * 1000))
            elif angle_deg is not None and distance_unit is not None:
                raise NotImplementedError()
            elif angle_deg is not None:
                if angle_deg == 0:
                    return

                min_wheel = self._wheels[self._min_wheel]
                max_wheel = self._wheels[self._max_wheel]
                min_wheel_speed = speeds_tacho[self._min_wheel]
                max_wheel_speed = speeds_tacho[self._max_wheel]

                if max_wheel_speed == 0:
                    radius = - max_wheel.offset
                elif min_wheel_speed == 0:
                    radius = - min_wheel.offset
                else:
                    ratio = min_wheel_speed / max_wheel_speed
                    radius = (min_wheel.offset - ratio * max_wheel.offset) / (ratio - 1)

                positions_tacho = []
                for i in range(len(speeds_tacho)):
                    wheel = self._wheels[i]
                    speed_tacho = speeds_tacho[i]
                    if speed_tacho == 0:
                        positions_tacho.append(0)
                        continue
                    circuit_unit = 2 * abs(radius + wheel.offset) * math.pi
                    position_unit = circuit_unit / 360 * angle_deg * (speed_tacho / abs(speed_tacho))
                    positions_tacho.append(position_unit * wheel.unit_ratio * wheel.total_ratio)

                for i in range(len(speeds_tacho)):
                    wheel = self._wheels[i]
                    speed_tacho = speeds_tacho[i]
                    if int(speed_tacho) == 0:
                        continue
                    position_tacho = positions_tacho[i]
                    wheel.motor.run_to_rel_pos(speed_sp=speed_tacho, position_sp=position_tacho)

            elif distance_unit is not None:
                if distance_unit == 0:
                    return

                min_wheel = self._wheels[self._min_wheel]
                max_wheel = self._wheels[self._max_wheel]
                min_wheel_speed = speeds_tacho[self._min_wheel]
                max_wheel_speed = speeds_tacho[self._max_wheel]

                speed_delta_per_offset_delta = \
                    (max_wheel_speed - min_wheel_speed) / (max_wheel.offset - min_wheel.offset)

                for i in range(len(speeds_tacho)):
                    wheel = self._wheels[i]
                    speed_tacho = speeds_tacho[i]
                    if int(speed_tacho) == 0:
                        continue
                    distance_tacho = distance_unit * wheel.unit_ratio * wheel.total_ratio
                    position = distance_tacho + (wheel.offset * speed_delta_per_offset_delta)
                    wheel.motor.run_to_rel_pos(speed_sp=speed_tacho, position_sp=position)
            else:
                for i in range(len(speeds_tacho)):
                    self._wheels[i].motor.run_forever(speed_sp=speeds_tacho[i])
        else:
            actions = []
            for i in range(len(speeds_tacho)):
                actions.append(MotorAction(self._wheels[i], speeds_tacho[i], max_duty_cycle))

            self._stop_coordinator()
            self._running_coordinator = DriveCoordinator(actions, time_len, angle_deg, distance_unit)
            self._running_coordinator.start()

    def _raw_run_drive_unit(self, time_len=None, angle_deg=None, distance_unit=None,
                            course_r=None, speed_unit=None, max_duty_cycle=100, async=False):
        self._raw_run_unit(time_len=time_len, angle_deg=angle_deg, distance_unit=distance_unit,
                           speeds_unit=self._course_r_to_speeds(course_r, speed_unit, self._max_speed_unit),
                           max_duty_cycle=max_duty_cycle, async=async)

    def _raw_run_percent_drive_unit(self, time_len=None, angle_deg=None, distance_unit=None,
                                    course_percent=None, speed_unit=None, speed_mul=1.0,
                                    max_duty_cycle=100, async=False):
        self._raw_run_unit(time_len=time_len, angle_deg=angle_deg, distance_unit=distance_unit,
                           speeds_unit=self._course_percent_to_speeds(course_percent, self._max_speed_unit, 0,
                                                                      speed_unit, speed_mul),
                           max_duty_cycle=max_duty_cycle, async=async)

    def run_timed(self, time_len: float, speeds_tacho: list = None, max_duty_cycle: int = 100, async: bool = False):
        self._raw_run_tacho(time_len=time_len, speeds_tacho=speeds_tacho,
                            max_duty_cycle=max_duty_cycle, async=async)

    def run_forever(self, speeds_tacho: list = None, max_duty_cycle: int = 100, async: bool = False):
        self._raw_run_tacho(speeds_tacho=speeds_tacho, max_duty_cycle=max_duty_cycle, async=async)

    def run_deg_timed(self, time_len: float, speeds_deg: list = None, max_duty_cycle: int = 100, async: bool = False):
        self._raw_run_deg(time_len=time_len, speeds_deg=speeds_deg,
                          max_duty_cycle=max_duty_cycle, async=async)

    def run_deg_forever(self, speeds_deg: list = None, max_duty_cycle: int = 100, async: bool = False):
        self._raw_run_deg(speeds_deg=speeds_deg, max_duty_cycle=max_duty_cycle, async=async)

    def run_unit_timed(self, time_len: float, speeds_unit: list = None, max_duty_cycle: int = 100,
                       async: bool = False):
        self._raw_run_unit(time_len=time_len, speeds_unit=speeds_unit,
                           max_duty_cycle=max_duty_cycle, async=async)

    def run_unit_forever(self, speeds_unit: list = None, max_duty_cycle: int = 100, async: bool = False):
        self._raw_run_unit(speeds_unit=speeds_unit, max_duty_cycle=max_duty_cycle, async=async)

    def run_drive_forever(self, course_r: float, speed_unit: float = None, max_duty_cycle: int = 100,
                          async: bool = False):
        self._raw_run_drive_unit(course_r=course_r, speed_unit=speed_unit, max_duty_cycle=max_duty_cycle, async=async)

    def run_drive_timed(self, time_len: float, course_r: float, speed_unit: float = None,
                        max_duty_cycle: int = 100, async: bool = False):
        self._raw_run_drive_unit(time_len=time_len, course_r=course_r, speed_unit=speed_unit,
                                 max_duty_cycle=max_duty_cycle, async=async)

    def run_drive_to_angle_deg(self, angle_deg: float, course_r: float, speed_unit: float = None,
                               max_duty_cycle: int = 100, async: bool = False):
        self._raw_run_drive_unit(angle_deg=angle_deg, course_r=course_r, speed_unit=speed_unit,
                                 max_duty_cycle=max_duty_cycle, async=async)

    def run_drive_to_distance(self, distance_unit: float, course_r: float, speed_unit: float = None,
                              max_duty_cycle: int = 100, async: bool = False):
        self._raw_run_drive_unit(distance_unit=distance_unit, course_r=course_r, speed_unit=speed_unit,
                                 max_duty_cycle=max_duty_cycle, async=async)

    def run_percent_drive_forever(self, course_percent: float, speed_unit: float = None, speed_mul: float = 1,
                                  max_duty_cycle: int = 100, async: bool = False):
        self._raw_run_percent_drive_unit(course_percent=course_percent, speed_unit=speed_unit, speed_mul=speed_mul,
                                         max_duty_cycle=max_duty_cycle, async=async)

    def run_percent_drive_timed(self, time_len: float, course_percent: float, speed_unit: float = None,
                                speed_mul: float = 1, max_duty_cycle: int = 100, async: bool = False):
        self._raw_run_percent_drive_unit(time_len=time_len, course_percent=course_percent, speed_unit=speed_unit,
                                         speed_mul=speed_mul, max_duty_cycle=max_duty_cycle, async=async)

    def run_percent_drive_to_angle_deg(self, angle_deg: float, course_percent: float, speed_unit: float = None,
                                       speed_mul: float = 1, max_duty_cycle: int = 100, async: bool = False):
        self._raw_run_percent_drive_unit(angle_deg=angle_deg, course_percent=course_percent, speed_unit=speed_unit,
                                         speed_mul=speed_mul, max_duty_cycle=max_duty_cycle, async=async)

    def run_percent_drive_to_distance(self, distance_unit: float, course_percent: float, speed_unit: float = None,
                                      speed_mul: float = 1, max_duty_cycle: int = 100, async: bool = False):
        self._raw_run_percent_drive_unit(distance_unit=distance_unit, course_percent=course_percent,
                                         speed_unit=speed_unit, speed_mul=speed_mul, max_duty_cycle=max_duty_cycle,
                                         async=async)

    def run_direct(self, course_percent: float = 0, target_duty_cycle: int = 100,
                   mul_duty_cycle: float = 1, min_duty_cycle: int = 0, max_duty_cycle: int = 0):
        duty_cycles = self._course_percent_to_speeds(course_percent, max_duty_cycle, min_duty_cycle,
                                                     target_duty_cycle, mul_duty_cycle)
        for i in range(len(self._wheels)):
            self._wheels[i].motor.run_direct(duty_cycle_sp=duty_cycles[i])

    def update_duty_cycle_raw(self, duty_cycles):
        self._validate_len(duty_cycles)
        for i in range(len(self._wheels)):
            wheel = self._wheels[i]
            wheel.motor.duty_cycle_sp = duty_cycles[i] * (abs(wheel.gear_ratio) / wheel.gear_ratio)

    def update_duty_cycle(self, course_percent: float, target_duty_cycle: int = 100,
                          mul_duty_cycle: float = 1, min_duty_cycle: int = 0, max_duty_cycle: int = 100):
        self.update_duty_cycle_raw(self._course_percent_to_speeds(course_percent, max_duty_cycle, min_duty_cycle,
                                                                  target_duty_cycle, mul_duty_cycle))

    def update_duty_cycle_unit(self, course_r: float, target_duty_cycle: int = None, max_duty_cycle: int = 100):
        self.update_duty_cycle_raw(self._course_r_to_speeds(course_r, target_duty_cycle, max_duty_cycle))

    def set_stop_action(self, stop_action: str):
        for wheel in self._wheels:
            wheel.stop_action = stop_action

    def restore_positions(self, positions: list, speed_unit=None):
        if speed_unit is None:
            speed_unit = self._max_speed_unit
        speed_tacho = self._speeds_deg_to_tacho(self._speeds_unit_to_deg([speed_unit]))[0]

        changes = []
        max_change = 0
        for i in range(len(positions)):
            change = positions[i] - self._wheels[i].motor.position
            changes.append(change)
            max_change = max(max_change, abs(change))

        if max_change > 0:
            self._validate_len(positions)
            for i in range(len(positions)):
                wheel_speed_tacho = speed_tacho / max_change * changes[i]
                self._wheels[i].motor.run_to_abs_pos(speed_sp=wheel_speed_tacho, position_sp=positions[i])

    def get_positions(self):
        positions = []
        for wheel in self._wheels:
            positions.append(wheel.motor.position)
        return positions

    def positions_change_to_angle(self, positions_change):  # TODO: test direction
        positions_change_len = len(positions_change)
        if positions_change_len != len(self._wheels):
            raise Exception('Invalid positions_change length.')

        if positions_change_len < 2 or self._wheels[self._min_wheel].offset == self._wheels[self._max_wheel].offset:
            return 0

        min_wheel = self._wheels[self._min_wheel]
        max_wheel = self._wheels[self._max_wheel]
        min_offset = min_wheel.offset
        max_offset = max_wheel.offset
        min_traveled = positions_change[self._min_wheel] / min_wheel.unit_ratio / min_wheel.total_ratio
        max_traveled = positions_change[self._max_wheel] / max_wheel.unit_ratio / max_wheel.total_ratio

        if abs(max_traveled) + abs(min_traveled) < 0.5:
            return 0

        if min_traveled == max_traveled:
            return 0
        elif max_traveled == 0:
            min_radius = min_offset - max_offset
            max_radius = 0
        elif min_traveled == 0:
            min_radius = 0
            max_radius = max_offset - min_offset
        else:
            ratio = min_traveled / max_traveled
            radius = (min_offset - ratio * max_offset) / (ratio - 1)
            min_radius = radius + min_offset
            max_radius = radius + max_offset

        if abs(min_radius) > abs(max_radius):
            circuit = 2 * min_radius * math.pi
            angle_deg = (min_traveled / circuit) * 360
        else:
            circuit = 2 * max_radius * math.pi
            angle_deg = (max_traveled / circuit) * 360

        return angle_deg

    def get_states(self):
        states = []
        for wheel in self._wheels:
            states.append(wheel.motor.state)
        return states

    def is_running(self):
        coordinator = self._running_coordinator
        if coordinator is not None and coordinator.is_alive():
            return True

        for wheel in self._wheels:
            if Motor.STATE_RUNNING in wheel.motor.state:
                return True

        return False

    def repeat_while_running_and_cond(self, method, cond_and=None, cond_or=None):
        while (self.is_running() and (cond_and is None or cond_and())) or (cond_or is not None and cond_or()):
            method()

    def wait_to_stop_and_cond(self, cond_and=None, cond_or=None):
        self.repeat_while_running_and_cond(lambda: time.sleep(0.05), cond_and, cond_or)

    def repeat_while_running(self, method):
        while self.is_running():
            method()

    def wait_to_stop(self):
        while True:
            coordinator = self._running_coordinator
            if coordinator is not None and coordinator.is_alive():
                coordinator.wait_to_stop()
                continue

            for wheel in self._wheels:
                if Motor.STATE_RUNNING in wheel.motor.state:
                    while Motor.STATE_RUNNING in wheel.motor.state:
                        time.sleep(0.1)
                    continue
            break

    def generate_json_info(self):
        return {
            'running': self.is_running(),
            'wheels': [
                wheel.generate_json_info() for wheel in self._wheels
            ]
        }
