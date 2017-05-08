import time

from ev3dev.auto import Motor


class ScannerPropulsionInfo:
    def __init__(self, gear_ratio: float, count_per_rot: int):
        self.gear_ratio = gear_ratio
        self.tacho_ratio = count_per_rot / 360
        self.total_ratio = self.gear_ratio * self.tacho_ratio

    def generate_json_info(self):
        return {
            'gear_ratio': self.gear_ratio,
            'tacho_ratio': self.tacho_ratio,
            'total_ratio': self.total_ratio
        }


class ScannerPropulsion:
    def __init__(self, motor: Motor, propulsion_info: ScannerPropulsionInfo):
        self._motor = motor
        self._propulsion_info = propulsion_info

    @property
    def motor(self):
        return self._motor

    @property
    def connected(self):
        return self._motor.connected

    @property
    def propulsion_info(self):
        return self._propulsion_info

    def reset(self):
        if not self.connected:
            return
        self.motor.stop_action = Motor.STOP_ACTION_BRAKE
        self.rotate_to_abs_pos(0, speed=self.motor.max_speed / 10)
        self.wait_to_stop()
        self.rotate_to_abs_pos(0, speed=self.motor.max_speed / 10)
        self.wait_to_stop()
        self.motor.reset()
        self.motor.stop_action = Motor.STOP_ACTION_BRAKE
        self.motor.ramp_up_sp = self.motor.max_speed / 2
        self.motor.ramp_down_sp = self.motor.max_speed / 2

    @property
    def is_running(self):
        return Motor.STATE_RUNNING in self.motor.state

    @property
    def angle_deg(self):
        return self.motor.position / self._propulsion_info.total_ratio

    @property
    def angle_rad(self):
        raise NotImplementedError()

    def _angle(self, angle: float):
        return angle * self._propulsion_info.total_ratio

    def _speed(self, speed: float = None):
        return self.motor.max_speed if speed is None else speed * self._propulsion_info.total_ratio

    def rotate_to_abs_pos(self, angle, speed: float = None):
        self.motor.run_to_abs_pos(speed_sp=self._speed(speed), position_sp=self._angle(angle))

    def rotate_to_rel_pos(self, angle, speed: float = None):
        self.motor.run_to_rel_pos(speed_sp=self._speed(speed), position_sp=self._angle(angle))

    def repeat_while_running(self, method):
        while self.is_running:
            method()

    def wait_to_stop(self):
        while Motor.STATE_RUNNING in self.motor.state:
            time.sleep(0.1)

    def generate_json_info(self):
        return {
            'motor': {
                'connected': self.connected,
                'angle_deg': self.angle_deg if self.motor.connected else 'unavailable',
                'speed': self.motor.speed if self.motor.connected else 'unavailable',
                'running': self.is_running if self.motor.connected else 'unavailable'
            },
            'propulsion_info': self._propulsion_info.generate_json_info()
        }
