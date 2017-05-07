# TODO: remove

# import math
#
# import numpy as np
#
# from utils.calc import dimensions as dp
# from utils.control.odometry import OdometryCalculator
# from utils.hardware.robot import Robot
# from utils.threading.cycle_thread import CycleThread
# from utils.utils import crop_m, list_line_points, list_circle_points
#
#
# class WorldMap:
#     FLAG_WALL = int('10000000', 2)
#     FLAG_BACON = int('01000000', 2)
#     FLAG_COL_RED = int('00100000', 2)
#     FLAG_COL_GREEN = int('00010000', 2)
#     FLAG_COL_BLUE = int('00001000', 2)
#     FLAG_LIGHT_AND_NOISE = int('00000111', 2)
#
#     FLAG_CLEAR_WALL = int('01111111', 2)
#     FLAG_CLEAR_BACON = int('10111111', 2)
#     FLAG_CLEAR_COL_RED = int('11011111', 2)
#     FLAG_CLEAR_COL_GREEN = int('11101111', 2)
#     FLAG_CLEAR_COL_BLUE = int('11110111', 2)
#     FLAG_CLEAR_LIGHT_AND_NOISE = int('11111000', 2)
#
#     def __init__(self, width: int, height: int):
#         self.contents = np.empty([width, height], dtype=np.byte)
#         self.shape = self.contents.shape
#         self.width = self.shape[0]
#         self.height = self.shape[1]
#
#     def get(self, x, y):
#         if x < 0 or y < 0 or x >= self.width or y >= self.height:
#             return 0
#         return self.contents[x][y]
#
#     def set(self, x, y, flag):
#         if x < 0 or y < 0 or x >= self.width or y >= self.height:
#             pass
#         self.contents[x][y] = self.contents[x][y] | flag
#
#     def clear(self, x, y, clear_flag):
#         if x < 0 or y < 0 or x >= self.width or y >= self.height:
#             pass
#         self.contents[x][y] = self.contents[x][y] & clear_flag
#
#     def wall(self, x: int, y: int) -> bool:
#         return bool(self.get(x, y) & self.FLAG_WALL)
#
#     def bacon(self, x: int, y: int) -> bool:
#         return bool(self.get(x, y) & self.FLAG_BACON)
#
#     def color_rgb(self, x: int, y: int) -> list:
#         pos_content = self.get(x, y)
#         return [
#             0 if pos_content & flag else 255 for flag in (self.FLAG_COL_RED, self.FLAG_COL_GREEN, self.FLAG_COL_BLUE)
#         ]
#
#     def light_and_noise(self, x: int, y: int) -> float:
#         return (self.get(x, y) & self.FLAG_LIGHT_AND_NOISE) / 7 * 100
#
#     def create_lines(self, points: list, flag: int):
#         for i in range(1, len(points)):
#             self.create_line(points[i - 1], points[i], flag)
#
#     def create_line(self, start, end, flag: int):
#         for point in list_line_points(start, end):
#             self.set(point[0], point[1], flag)
#
#     def create_circle(self, x: float, y: float, r: float, flag: int, start_angle: float = 0, stop_angle: float = 360):
#         for point in list_circle_points(x, y, r, start_angle=start_angle, stop_angle=stop_angle):
#             self.set(point[0], point[1], flag)
#
#
# class World:
#     def __init__(self, world_map: WorldMap, robot: Robot):
#         self.robot = robot
#         self.map = world_map
#         self._position = dp.Position(dp.Point(0, 0, 0), dp.Angle())
#
#         if not self.robot.simulation_enabled:
#             self._odometry = None
#             self._odometry_thread = None
#         else:
#             wheels = self.robot.bricks.wheels_bricks()
#             left_wheel_brick = min(
#                 wheels, key=lambda wheel_brick: wheel_brick.wheel_info.position.point.x, default=None)
#             right_wheel_brick = max(
#                 wheels, key=lambda wheel_brick: wheel_brick.wheel_info.position.point.x, default=None)
#             if left_wheel_brick is None or right_wheel_brick is None\
#                     or left_wheel_brick.wheel_info.position.point.x == right_wheel_brick.wheel_info.position.point.x:
#                 self._odometry = None
#                 self._odometry_thread = None
#             else:
#                 distance_between_wheels =\
#                     right_wheel_brick.wheel_info.position.x - left_wheel_brick.wheel_info.position.x
#                 self._odometry = OdometryCalculator(
#                     lambda: left_wheel_brick.position.angle.angle_y_rad,
#                     lambda: right_wheel_brick.position.angle.angle_y_rad,
#                     distance_between_wheels
#                 )
#
#                 def odometry_cycle():
#                     self._odometry.cycle()
#                     odometry_pos = self._odometry.position
#
#                     self._position.point.x = odometry_pos[0]
#                     self._position.point.y = odometry_pos[1]
#                     self._position.angle.angle_z_rad = odometry_pos[2]
#
#                 self._odometry_thread = CycleThread(target=odometry_cycle, sleep_time=0.02,
#                                                     name='OdometryThread', daemon=True)
#                 self._odometry_thread.start()
#
#     @property
#     def position(self) -> dp.Position:
#         return self._position
#
#     @position.setter
#     def position(self, position: dp.Position):
#         if self._odometry is not None:
#             self._odometry.position = [position.point.x, position.point.y, position.angle.angle_z_rad]
#         self._position = position
#
#     def _offset_pos(self, move: dp.Point = None, rotate_view: dp.Angle = None):
#         if move is None and rotate_view is None:
#             return self.position
#
#         position = self.position.copy()
#         if move is not None:
#             position.point.move(move.copy().rotate(position.angle))
#         if rotate_view is not None:
#             position.angle.rotate(rotate_view)
#         return position
#
#     @staticmethod
#     def _nearest_places_from(point: dp.Point):
#         result = []
#         for methods in [[math.floor, math.floor], [math.floor, math.ceil],
#                         [math.ceil, math.floor], [math.ceil, math.ceil]]:
#             pos = [methods[0](point.x), methods[1](point.y)]
#             distance = math.sqrt((point.x - pos[0]) ** 2 + (point.y - pos[1]) ** 2)
#             place = [pos, distance]
#             if place not in result:
#                 result.append(place)
#         return result
#
#     def color_rgb_on_pos(self, move: dp.Point = None, rotate_view: dp.Angle = None) -> list:
#         nearest_places = self._nearest_places_from(self._offset_pos(move, rotate_view))
#         colors = [[col * place[1] for col in self.map.color_rgb(place[0][0], place[0][1])] for place in nearest_places]
#         total = sum((1 - place[1] for place in nearest_places))
#         return [crop_m(sum((color[pos] for color in colors)) / total, 0, 255) for pos in range(3)]
#
#     def reflect_on_pos(self, move: dp.Point = None, rotate_view: dp.Angle = None) -> float:
#         color = self.color_rgb_on_pos(move, rotate_view)
#         return crop_m(sum(color) / len(color) / 255 * 100, 0, 100)
#
#     def light_on_pos(self, move: dp.Point = None, rotate_view: dp.Angle = None) -> float:
#         nearest_places = self._nearest_places_from(self._offset_pos(move, rotate_view))
#         lights = [self.map.light_and_noise(place[0][0], place[0][1]) * place[1] for place in nearest_places]
#         total = sum((1 - place[1] for place in nearest_places))
#         return crop_m(sum(lights) / total, 0, 100)
#
#     def distance_from_wall_on_pos(self, move: dp.Point = None, rotate_view: dp.Angle = None) -> float:
#         return math.inf  # TODO: implement
#
#     def beacon_pos_offset(self, move: dp.Point = None, rotate_view: dp.Angle = None) -> float or None:
#         return None  # TODO: implement
#
#     def pos_in_wall(self, move: dp.Point = None, rotate_view: dp.Angle = None) -> bool:
#         nearest_places = self._nearest_places_from(self._offset_pos(move, rotate_view))
#         return any([self.map.wall(place[0][0], place[0][1]) for place in nearest_places])
#
#     def noise_on_pos(self, move: dp.Point = None, rotate_view: dp.Angle = None, use_a_weighting=False) -> float:
#         # TODO support for a weighting
#         nearest_places = self._nearest_places_from(self._offset_pos(move, rotate_view))
#         noises = [self.map.light_and_noise(place[0][0], place[0][1]) * place[1] for place in nearest_places]
#         total = sum((1 - place[1] for place in nearest_places))
#         return crop_m(sum(noises) / total, 0, 100)
