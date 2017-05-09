import math
import unittest

from utils.calc import dimensions as dp
from utils.hardware.simulation.world import World
from utils.hardware.simulation.world_map import WorldMap


class TestWorld(unittest.TestCase):
    def setUp(self):
        self.world_map = WorldMap(700, 700)
        flag_black_color = WorldMap.FLAG_COL_RED | WorldMap.FLAG_COL_GREEN | WorldMap.FLAG_COL_BLUE
        self.world_map.create_lines([
            (100, 300), (500, 300), (550, 350), (550, 400), (500, 450),
            (100, 450), (50, 400), (50, 350), (100, 300)
        ], flag_black_color)

        self.robot_position = dp.Position(dp.Point(300, 300, 0), dp.Angle(rad_z=math.radians(90)))
        self.world = World(self.robot_position, self.world_map)

    def test_read(self):
        for point, angle in (
                (None, None),
                (dp.Point(0, 0, 0), dp.Angle()),
                (dp.Point(0, 0, 0), dp.Angle()),
                (dp.Point(50, 0, 0), dp.Angle()),
                (dp.Point(0, 50, 0), dp.Angle())):
            pos = self.world.pos_on_pos(point, angle)
            rgb_world = self.world.color_rgb_on_pos(point, angle)
            rgb_map = self.world_map.color_rgb(int(pos.point.x), int(pos.point.y))
            print(rgb_map, rgb_world, pos)


if __name__ == '__main__':
    unittest.main()
