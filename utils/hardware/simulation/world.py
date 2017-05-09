import math

from utils.calc import dimensions as dp
from utils.hardware.simulation.world_map import WorldMap
from utils.utils import crop_m


class World:
    def __init__(self, robot_position: dp.Position, world_map: WorldMap):
        self.map = world_map
        self._robot_position = robot_position

    def _offset_pos(self, move: dp.Point = None, rotate_view: dp.Angle = None):
        if move is None and rotate_view is None:
            return self._robot_position.copy()

        position = self._robot_position.copy()
        if move is not None:
            position.point.move(move.copy().rotate(position.angle))
        if rotate_view is not None:
            position.angle.rotate(rotate_view)
        return position

    @staticmethod
    def _nearest_places_from(point: dp.Point):
        places = []
        for methods in [[math.floor, math.floor], [math.floor, math.ceil],
                        [math.ceil, math.floor], [math.ceil, math.ceil]]:
            pos = [methods[0](point.x), methods[1](point.y)]
            distance = math.sqrt((point.x - pos[0]) ** 2 + (point.y - pos[1]) ** 2)
            place = [pos, 1.5 - distance]
            if place not in places:
                places.append(place)
        return places

    def pos_on_pos(self, move: dp.Point = None, rotate_view: dp.Angle = None) -> dp.Position:
        return self._offset_pos(move, rotate_view)

    def color_rgb_on_pos(self, move: dp.Point = None, rotate_view: dp.Angle = None) -> list:
        nearest_places = self._nearest_places_from(self._offset_pos(move, rotate_view).point)
        colors = [[col * place[1] for col in self.map.color_rgb(place[0][0], place[0][1])] for place in nearest_places]
        total = sum((place[1] for place in nearest_places))
        return [crop_m(sum((color[pos] for color in colors)) / total, 0, 255) for pos in range(3)]

    def reflect_on_pos(self, move: dp.Point = None, rotate_view: dp.Angle = None) -> float:
        color = self.color_rgb_on_pos(move, rotate_view)
        return crop_m(sum(color) / len(color) / 255 * 100, 0, 100)

    def light_on_pos(self, move: dp.Point = None, rotate_view: dp.Angle = None) -> float:
        nearest_places = self._nearest_places_from(self._offset_pos(move, rotate_view).point)
        lights = [self.map.light_and_noise(place[0][0], place[0][1]) * place[1] for place in nearest_places]
        total = sum((place[1] for place in nearest_places))
        return crop_m(sum(lights) / total, 0, 100)

    def distance_from_wall_on_pos(self, move: dp.Point = None, rotate_view: dp.Angle = None) -> float:
        return math.inf  # TODO: implement

    def beacon_pos_offset(self, move: dp.Point = None, rotate_view: dp.Angle = None) -> float or None:
        return None  # TODO: implement

    def pos_in_wall(self, move: dp.Point = None, rotate_view: dp.Angle = None) -> bool:
        nearest_places = self._nearest_places_from(self._offset_pos(move, rotate_view).point)
        return any([self.map.wall(place[0][0], place[0][1]) for place in nearest_places])

    def noise_on_pos(self, move: dp.Point = None, rotate_view: dp.Angle = None, use_a_weighting=False) -> float:
        # TODO support for a weighting
        nearest_places = self._nearest_places_from(self._offset_pos(move, rotate_view).point)
        noises = [self.map.light_and_noise(place[0][0], place[0][1]) * place[1] for place in nearest_places]
        total = sum((place[1] for place in nearest_places))
        return crop_m(sum(noises) / total, 0, 100)
