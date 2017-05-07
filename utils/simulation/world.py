import math

import numpy as np
from utils.calc.position import Position2D
from utils.hardware.robot import Robot

from utils.control.odometry import OdometryWheel, OdometryCalculator
from utils.simulation.world_effect import WheelEffect
from utils.threading.cycle_thread import CycleThread
from utils.utils import crop_m, list_line_points, list_circle_points


class WorldMap:
    FLAG_WALL = int('10000000', 2)
    FLAG_BACON = int('01000000', 2)
    FLAG_COL_RED = int('00100000', 2)
    FLAG_COL_GREEN = int('00010000', 2)
    FLAG_COL_BLUE = int('00001000', 2)
    FLAG_LIGHT_AND_NOISE = int('00000111', 2)

    FLAG_CLEAR_WALL = int('01111111', 2)
    FLAG_CLEAR_BACON = int('10111111', 2)
    FLAG_CLEAR_COL_RED = int('11011111', 2)
    FLAG_CLEAR_COL_GREEN = int('11101111', 2)
    FLAG_CLEAR_COL_BLUE = int('11110111', 2)
    FLAG_CLEAR_LIGHT_AND_NOISE = int('11111000', 2)

    def __init__(self, width: int, height: int):
        self.contents = np.empty([width, height], dtype=np.byte)
        self.shape = self.contents.shape
        self.width = self.shape[0]
        self.height = self.shape[1]

    def get(self, x, y):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return 0
        return self.contents[x][y]

    def set(self, x, y, flag):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            pass
        self.contents[x][y] = self.contents[x][y] | flag

    def clear(self, x, y, clear_flag):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            pass
        self.contents[x][y] = self.contents[x][y] & clear_flag

    def wall(self, x: int, y: int) -> bool:
        return bool(self.get(x, y) & self.FLAG_WALL)

    def bacon(self, x: int, y: int) -> bool:
        return bool(self.get(x, y) & self.FLAG_BACON)

    def color_rgb(self, x: int, y: int) -> list:
        pos_content = self.get(x, y)
        return [
            0 if pos_content & flag else 255 for flag in (self.FLAG_COL_RED, self.FLAG_COL_GREEN, self.FLAG_COL_BLUE)
        ]

    def light_and_noise(self, x: int, y: int) -> float:
        return (self.get(x, y) & self.FLAG_LIGHT_AND_NOISE) / 7 * 100

    def create_lines(self, points: list, flag: int):
        for i in range(1, len(points)):
            self.create_line(points[i - 1], points[i], flag)

    def create_line(self, start, end, flag: int):
        for point in list_line_points(start, end):
            self.set(point[0], point[1], flag)

    def create_circle(self, x: float, y: float, r: float, flag: int, start_angle: float = 0, stop_angle: float = 360):
        for point in list_circle_points(x, y, r, start_angle=start_angle, stop_angle=stop_angle):
            self.set(point[0], point[1], flag)


class World:
    def __init__(self, world_map: WorldMap, robot: Robot):
        self._robot = robot
        self._map = world_map
        self._position = Position2D(0, 0, 0)

        self._bind_done = False
        self._effects = []
        self._odometry = None
        self._odometry_thread = None

    @property
    def robot(self):
        return self._robot

    @property
    def world_map(self):
        return self._map

    @property
    def position(self) -> Position2D:
        return self._position

    @position.setter
    def position(self, position: Position2D):
        if self._odometry is not None:
            self._odometry.position = [position.x, position.y, position.angle_rad]
        self._position = position

    @property
    def effects(self):
        return self.effects

    def bind_simulated_environment(self, simulated_environment):
        if self._bind_done:
            raise Exception()
        self._bind_done = True

        wheels = []
        for driver in simulated_environment.drivers:
            for world_effect in driver.interface.world_effects:
                self._effects.append([world_effect, driver])
                if isinstance(world_effect, WheelEffect):
                    wheels.append(OdometryWheel(world_effect.wheel_info, lambda: int(driver.position)))

        if len(wheels) > 0:
            self._start_odometry(*wheels)

    def _start_odometry(self, *wheels: OdometryWheel):
        if self._odometry_thread is not None or self._odometry is not None:
            raise Exception('Odometry is still running.')
        self._odometry = OdometryCalculator(*wheels)

        def odometry_cycle():
            self._odometry.cycle()
            odometry_pos = self._odometry.position
            self._position = Position2D(odometry_pos[0], odometry_pos[1], math.degrees(odometry_pos[2]))

        self._odometry_thread = CycleThread(target=odometry_cycle, sleep_time=0.02,
                                            name='OdometryThread', daemon=True)
        self._odometry_thread.start()

    def _offset_pos(self, offset: Position2D):
        if offset is None:
            return self.position
        return self.position.move_by(offset).rotate_by(offset.angle_deg)

    def _nearest_places_from(self, position: Position2D):
        result = []
        for methods in [[math.floor, math.floor], [math.floor, math.ceil],
                        [math.ceil, math.floor], [math.ceil, math.ceil]]:
            pos = [methods[0](position.x), methods[1](position.y)]
            distance = math.sqrt((position.x - pos[0]) ** 2 + (position.y - pos[1]) ** 2)
            place = [pos, distance]
            if place not in result:
                result.append(place)
        return result

    def color_rgb_on_pos(self, offset: Position2D = None) -> list:
        nearest_places = self._nearest_places_from(self._offset_pos(offset))
        colors = [[col * place[1] for col in self._map.color_rgb(place[0][0], place[0][1])] for place in nearest_places]
        total = sum((1 - place[1] for place in nearest_places))
        return [crop_m(sum((color[pos] for color in colors)) / total, 0, 255) for pos in range(3)]

    def reflect_on_pos(self, offset: Position2D = None) -> float:
        color = self.color_rgb_on_pos(offset)
        return crop_m(sum(color) / len(color) / 255 * 100, 0, 100)

    def light_on_pos(self, offset: Position2D = None) -> float:
        nearest_places = self._nearest_places_from(self._offset_pos(offset))
        lights = [self._map.light_and_noise(place[0][0], place[0][1]) * place[1] for place in nearest_places]
        total = sum((1 - place[1] for place in nearest_places))
        return crop_m(sum(lights) / total, 0, 100)

    def distance_from_wall_on_pos(self, offset: Position2D = None) -> float:
        return math.inf  # TODO: implement

    def beacon_pos_offset(self, offset: Position2D = None) -> float or None:
        return None  # TODO: implement

    def pos_in_wall(self, offset: Position2D = None) -> bool:
        nearest_places = self._nearest_places_from(self._offset_pos(offset))
        return any([self._map.wall(place[0][0], place[0][1]) for place in nearest_places])

    def noise_on_pos(self, offset: Position2D = None, use_a_weighting=False) -> float:  # TODO support for a weighting
        nearest_places = self._nearest_places_from(self._offset_pos(offset))
        noises = [self._map.light_and_noise(place[0][0], place[0][1]) * place[1] for place in nearest_places]
        total = sum((1 - place[1] for place in nearest_places))
        return crop_m(sum(noises) / total, 0, 100)
