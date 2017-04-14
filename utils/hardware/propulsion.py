import time

from ev3dev.auto import Motor


class ScannerPropulsion:
    def __init__(self, motor: Motor, gear_ratio: float):
        self._motor = motor
        self._gear_ratio = gear_ratio
        self._tacho_ratio = motor.count_per_rot / 360 if motor.connected else 1
        self._total_ratio = self._gear_ratio * self._tacho_ratio

    @property
    def motor(self):
        return self._motor

    @property
    def connected(self):
        return self._motor.connected

    @property
    def gear_ratio(self):
        return self._gear_ratio

    @property
    def tacho_ratio(self):
        return self._tacho_ratio

    @property
    def total_ratio(self):
        return self._total_ratio

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
        return self.motor.position / self.total_ratio

    @property
    def angle_rad(self):
        raise NotImplementedError()

    def _angle(self, angle: float):
        return angle * self.total_ratio

    def _speed(self, speed: float = None):
        return self.motor.max_speed if speed is None else speed * self.total_ratio

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
            'gear_ratio': self.gear_ratio,
            'tacho_ratio': self.tacho_ratio,
            'total_ratio': self.total_ratio
        }
