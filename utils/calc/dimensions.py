import math


class Point:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def __copy__(self):
        return self.copy()

    def copy(self):
        return Point(self.x, self.y, self.z)

    def negate(self):
        self.x, self.y, self.z = -self.x, -self.y, -self.z
        return self

        # def reset(self):
        #     self.x = 0
        #     self.y = 0
        #     self.z = 0


class Angle:
    def __init__(self, rad_z: float = 0, rad_x: float = 0, rad_y: float = 0):
        self.rad_z = rad_z
        self.rad_x = rad_x
        self.rad_y = rad_y

    @property
    def deg_z(self):
        return math.degrees(self.rad_z)

    @property
    def deg_x(self):
        return math.degrees(self.rad_x)

    @property
    def deg_y(self):
        return math.degrees(self.rad_y)

    def __copy__(self):
        return self.copy()

    def copy(self):
        return Angle(self.rad_z, self.rad_x, self.rad_y)

    def negate(self):
        self.rad_z, self.rad_x, self.rad_y = \
            -self.rad_z, -self.rad_x, -self.rad_y
        return self

        # def reset(self):
        #     self.angle_z_rad = 0
        #     self.angle_x_rad = 0
        #     self.angle_y_rad = 0


class Position:
    def __init__(self, point: Point, angle: Angle):
        self.point = point
        self.angle = angle

    def __copy__(self):
        return self.copy()

    def copy(self):
        return Position(self.point.copy(), self.angle.copy())

    def negate(self):
        self.point.negate()
        self.angle.negate()

        # def reset(self):
        #     self.point.reset()
        #     self.angle.reset()


def move(point: Point, vector: Point) -> Point:
    point.x += vector.x
    point.y += vector.y
    point.z += vector.z
    return point


def distance(point1: Point, point2: Point = None) -> float:
    if point2 is None:
        diff_x = point1.x ** 2
        diff_y = point1.y ** 2
        diff_z = point1.z ** 2
    else:
        diff_x = (point1.x - point2.x) ** 2
        diff_y = (point1.y - point2.y) ** 2
        diff_z = (point1.z - point2.z) ** 2

    return math.sqrt(diff_x + diff_y + diff_z)


def rotate_point(point: Point, angle: Angle, around: Point = None) -> Point:
    x, y, z = point.x, point.y, point.z
    angle_z_rad, angle_x_rad, angle_y_rad = \
        angle.rad_z, angle.rad_x, angle.rad_y

    if around is not None:
        x -= around.x
        y -= around.y
        z -= around.z

    if angle_z_rad != 0:
        angle_rad_cos = math.cos(angle_z_rad)
        angle_rad_sin = math.sin(angle_z_rad)
        _x = x * angle_rad_cos - y * angle_rad_sin
        _y = y * angle_rad_cos + x * angle_rad_sin
        x = _x
        y = _y
    if angle_x_rad != 0:
        angle_rad_cos = math.cos(angle_x_rad)
        angle_rad_sin = math.sin(angle_x_rad)
        _y = y * angle_rad_cos - z * angle_rad_sin
        _z = z * angle_rad_cos + y * angle_rad_sin
        y = _y
        z = _z
    if angle_y_rad != 0:
        angle_rad_cos = math.cos(angle_y_rad)
        angle_rad_sin = math.sin(angle_y_rad)
        _z = z * angle_rad_cos - x * angle_rad_sin
        _x = x * angle_rad_cos + z * angle_rad_sin
        z = _z
        x = _x

    point.x, point.y, point.z = x, y, z
    return point


def rotate_angle(angle: Angle, by: Angle) -> Angle:  # FIXME: not working properly
    angle.rad_z += by.rad_z
    angle.rad_x += by.rad_x
    angle.rad_y += by.rad_y
    return angle


Point.move = lambda self, vector: move(self, vector)
Point.distance = lambda self, target=None: distance(self, target)
Point.rotate = lambda self, angle, around=None: rotate_point(self, angle, around)

Angle.rotate = lambda self, by: rotate_angle(self, by)
