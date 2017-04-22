from utils.simulation.world import WorldMap

WORLD_MAP = WorldMap(500, 500)

flag_black_color = WORLD_MAP.FLAG_COL_RED | WORLD_MAP.FLAG_COL_GREEN | WORLD_MAP.FLAG_COL_BLUE
WORLD_MAP.create_lines([
    (-200, 0), (200, 0), (250, 50), (250, 100), (200, 150),
    (-200, 150), (-250, 100), (-250, 50), (-200, 0)
], flag_black_color)
del flag_black_color
