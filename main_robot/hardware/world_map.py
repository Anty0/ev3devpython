from utils.hardware.simulation.world_map import WorldMap

WORLD_MAP = WorldMap(700, 700)

flag_black_color = WORLD_MAP.FLAG_COL_RED | WORLD_MAP.FLAG_COL_GREEN | WORLD_MAP.FLAG_COL_BLUE
WORLD_MAP.create_lines([
    (100, 300), (500, 300), (550, 350), (550, 400), (500, 450),
    (100, 450), (50, 400), (50, 350), (100, 300)
], flag_black_color)
del flag_black_color
