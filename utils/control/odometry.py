import math
import time
from threading import Lock

from utils.hardware.wheel import Wheel


class OdometryCalculator:
    def __init__(self, left_wheel_traveled_distance_getter: callable,
                 right_wheel_traveled_distance_getter: callable,
                 distance_between_wheels: float):
        self._left_traveled_getter = left_wheel_traveled_distance_getter
        self._right_traveled_getter = right_wheel_traveled_distance_getter
        self._distance_between_wheels = distance_between_wheels

        self._lock = Lock()
        self._last_time = time.time()
        self._last_left_traveled = self._left_traveled_getter()
        self._last_right_traveled = self._right_traveled_getter()

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

            pos_left = self._left_traveled_getter()
            pos_right = self._right_traveled_getter()

            delta_left = pos_left - self._last_left_traveled
            delta_right = pos_right - self._last_right_traveled

            v_left = delta_left / time_change
            v_right = delta_right / time_change

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
            self._last_left_traveled = pos_left
            self._last_right_traveled = pos_right


def from_wheels(*wheels: Wheel) -> OdometryCalculator:
    left_wheel = min(wheels, key=lambda wheel: wheel.offset, default=None)
    right_wheel = max(wheels, key=lambda wheel: wheel.offset, default=None)
    if left_wheel is None or right_wheel is None or \
                    left_wheel.info.position.point.x == right_wheel.info.position.point.x:
        raise Exception('Invalid wheels input. Required two wheels with different offset at last.')

    left_motor = left_wheel.motor
    right_motor = right_wheel.motor
    distance_between_wheels = right_wheel.info.position.point.x - left_wheel.info.position.point.x
    left_motor_distance_per_tacho_count = (left_wheel.info.total_ratio * left_wheel.info.unit_ratio) ** -1
    right_motor_distance_per_tacho_count = (right_wheel.info.total_ratio * right_wheel.info.unit_ratio) ** -1
    return OdometryCalculator(
        lambda: left_motor.position * left_motor_distance_per_tacho_count,
        lambda: right_motor.position * right_motor_distance_per_tacho_count,
        distance_between_wheels
    )


class PositionsCollector:
    def __init__(self, odometry_calculator: OdometryCalculator):
        self.odometry_calculator = odometry_calculator
        self.positions = []

    def cycle(self):
        self.positions.append(self.odometry_calculator.position)
