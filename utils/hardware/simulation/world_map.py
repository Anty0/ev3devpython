from utils.utils import list_line_points, list_circle_points


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
        import numpy as np
        self.contents = np.empty([width, height], dtype=np.byte)
        self.contents.fill(0)
        self.changes = []
        self.shape = self.contents.shape
        self.width = self.shape[0]
        self.height = self.shape[1]

    def get(self, x, y):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return 0
        return self.contents[x][y]

    def get_filtered(self, x, y, flag):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return 0
        return self.contents[x][y] & flag

    def set(self, x, y, flag):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            pass
        self.contents[x][y] = self.contents[x][y] | flag
        self.changes.append(((x, y), self.contents[x][y]))

    def clear(self, x, y, clear_flag):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            pass
        self.contents[x][y] = self.contents[x][y] & clear_flag
        self.changes.append(((x, y), self.contents[x][y]))

    def wall(self, x: int, y: int) -> bool:
        return bool(self.get_filtered(x, y, self.FLAG_WALL))

    def bacon(self, x: int, y: int) -> bool:
        return bool(self.get_filtered(x, y, self.FLAG_BACON))

    def color_rgb(self, x: int, y: int) -> list:
        pos_content = self.get(x, y)
        return [
            0 if pos_content & flag else 255 for flag in (self.FLAG_COL_RED, self.FLAG_COL_GREEN, self.FLAG_COL_BLUE)
        ]

    def light_and_noise(self, x: int, y: int) -> float:
        return self.get_filtered(x, y, self.FLAG_LIGHT_AND_NOISE) / 7 * 100

    def create_lines(self, points: list, flag: int):
        for i in range(1, len(points)):
            self.create_line(points[i - 1], points[i], flag)

    def create_line(self, start, end, flag: int):
        for point in list_line_points(start, end):
            self.set(point[0], point[1], flag)

    def create_circle(self, x: float, y: float, r: float, flag: int, start_angle: float = 0, stop_angle: float = 360):
        for point in list_circle_points(x, y, r, start_angle=start_angle, stop_angle=stop_angle):
            self.set(point[0], point[1], flag)
