import unittest

from utils.hardware.simulation.world_map import WorldMap


class TestWorldMap(unittest.TestCase):
    def test_empty_map(self):
        test_width = test_height = 200
        world_map = WorldMap(test_width, test_height)
        self.assertEqual(world_map.width, test_width)
        self.assertEqual(world_map.height, test_height)

        for x in range(world_map.width):
            for y in range(world_map.height):
                map_point = world_map.get(x, y)
                self.assertEqual(map_point, 0)


if __name__ == '__main__':
    unittest.main()
