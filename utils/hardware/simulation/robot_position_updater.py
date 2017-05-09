import math

from utils.calc import dimensions as dp
from utils.control.odometry import OdometryCalculator
from utils.hardware.brick.base import WheelBrick
from utils.hardware.brick.bricks import Bricks
from utils.hardware.simulation.brick_controller import BricksControllers
from utils.threading.cycle_thread import CycleThread


class RobotPositionUpdater:
    def __init__(self, bricks: Bricks, bricks_controllers: BricksControllers, robot_position: dp.Position):
        self._bricks_controllers = bricks_controllers
        self._position = robot_position

        wheels = bricks.bricks_of_type(WheelBrick)
        left_wheel_brick = min(
            wheels, key=lambda wheel_brick: wheel_brick.wheel_info.position.point.x, default=None)
        right_wheel_brick = max(
            wheels, key=lambda wheel_brick: wheel_brick.wheel_info.position.point.x, default=None)
        if left_wheel_brick is None or right_wheel_brick is None \
                or left_wheel_brick.wheel_info.position.point.x == right_wheel_brick.wheel_info.position.point.x:
            self._odometry = None
            self._odometry_thread = None
        else:
            distance_between_wheels = \
                right_wheel_brick.wheel_info.position.point.x - left_wheel_brick.wheel_info.position.point.x
            self._odometry = OdometryCalculator(
                lambda:
                left_wheel_brick.position.get(self._bricks_controllers).angle.rad_y /
                left_wheel_brick.wheel_info.unit_ratio_rad
                # [print('Left: ', self._bricks_controllers.brick_controller(left_wheel_brick).position,
                #        left_wheel_brick.position.get(self._bricks_controllers).angle),
                #  left_wheel_brick.position.get(self._bricks_controllers).angle.rad_x /
                #  left_wheel_brick.wheel_info.unit_ratio_rad][1]
                ,

                lambda:
                right_wheel_brick.position.get(self._bricks_controllers).angle.rad_y /
                right_wheel_brick.wheel_info.unit_ratio_rad
                # [print('Right: ', self._bricks_controllers.brick_controller(right_wheel_brick).position,
                #        right_wheel_brick.position.get(self._bricks_controllers).angle),
                #  right_wheel_brick.position.get(self._bricks_controllers).angle.rad_x /
                #  right_wheel_brick.wheel_info.unit_ratio_rad][1]
                ,

                distance_between_wheels
            )
            self._odometry.position = [self._position.point.x, self._position.point.y,
                                       -(self._position.angle.rad_z + math.pi / 2)]

            self._odometry_thread = CycleThread(target=self._odometry_cycle, sleep_time=0.02,
                                                name='OdometryThread', daemon=True)
            self._odometry_thread.start()

    def _odometry_cycle(self):
        self._odometry.cycle()
        odometry_pos = self._odometry.position

        self._position.point.x = odometry_pos[0]
        self._position.point.y = odometry_pos[1]
        self._position.angle.rad_z = -(odometry_pos[2] + math.pi / 2)

    @property
    def odometry(self) -> OdometryCalculator:
        return self._odometry

    @property
    def position(self) -> dp.Position:
        return self._position

    @position.setter
    def position(self, position: dp.Position):
        position = position.copy()
        if self._odometry is not None:
            self._odometry.position = [position.point.x, position.point.y,
                                       -(position.angle.rad_z + math.pi / 2)]
        self._position.point = position.point
        self._position.angle = position.angle
