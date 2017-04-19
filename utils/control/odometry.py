import math
import time
from threading import Lock

from utils.hardware.wheel import Wheel


class OdometryCalculator:
    def __init__(self, *wheels: Wheel):
        left_wheel = min(wheels, key=lambda wheel: wheel.offset, default=None)
        right_wheel = max(wheels, key=lambda wheel: wheel.offset, default=None)
        if left_wheel is None or right_wheel is None or left_wheel.offset == right_wheel.offset:
            raise Exception('Invalid wheels input. Required two wheels with different offset at last.')

        self._left_motor = left_wheel.motor
        self._right_motor = right_wheel.motor
        self._distance_between_wheels = right_wheel.offset - left_wheel.offset
        self._left_motor_distance_per_tacho_count = (left_wheel.total_ratio * left_wheel.unit_ratio) ** -1
        self._right_motor_distance_per_tacho_count = (right_wheel.total_ratio * right_wheel.unit_ratio) ** -1

        self._lock = Lock()
        self._last_time = time.time()
        self._last_left_position = self._left_motor.position
        self._last_right_position = self._right_motor.position

        self._x = 0
        self._y = 0
        self._angle_rad = 0

    @property
    def position(self):
        with self._lock:
            return self._x, self._y, self._angle_rad

    @position.setter
    def position(self, val: list):
        with self._lock:
            self._x = val[0]
            self._y = val[1]
            self._angle_rad = val[2]

    def cycle(self):
        with self._lock:
            last_time = self._last_time
            current_time = time.time()
            time_change = current_time - last_time

            pos_left = self._left_motor.position
            pos_right = self._right_motor.position

            delta_left = pos_left - self._last_left_position
            delta_right = pos_right - self._last_right_position

            v_left = (delta_left * self._left_motor_distance_per_tacho_count) / time_change
            v_right = (delta_right * self._right_motor_distance_per_tacho_count) / time_change

            vx = (v_right + v_left) / 2
            v_angle = (v_right - v_left) / self._distance_between_wheels

            last_angle = self._angle_rad
            delta_x = (vx * math.cos(last_angle)) * time_change
            delta_y = (vx * math.sin(last_angle)) * time_change
            delta_angle = v_angle * time_change

            self._x += delta_x
            self._y += delta_y
            self._angle_rad += delta_angle

            self._last_time = current_time
            self._last_left_position = pos_left


class PositionsCollector:
    def __init__(self, odometry_calculator: OdometryCalculator):
        self.odometry_calculator = odometry_calculator
        self.positions = []

    def cycle(self):
        self.positions.append(self.odometry_calculator.position)
