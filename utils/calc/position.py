import math


class Position2D:
    def __init__(self, x: float, y: float, angle_deg: float):
        self._x = x
        self._y = y
        self._angle_deg = angle_deg

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def angle_deg(self):
        return self._angle_deg

    @property
    def angle_rad(self):
        return math.radians(self._angle_deg)

    def __add__(self, other):
        if isinstance(other, Position2D):
            x = other.x,
            y = other.y,
            angle_deg = other.angle_deg
        elif isinstance(other, list) and len(other) == 3:
            x = other[0]
            y = other[1]
            angle_deg = other[2]
        else:
            raise Exception('Can\'t add unknown object to Position2D.')
        return Position2D(self.x + x, self.y + y,
                          self.angle_deg + angle_deg)

    def __neg__(self):
        return self.negative()

    def move_by(self, position):
        if self.angle_deg == 0:
            return Position2D(self.x + position.x, self.y + position.y, self.angle_deg)
        else:
            rot_angle_rad = self.angle_rad
            rot_angle_rad_cos = math.cos(rot_angle_rad)
            rot_angle_rad_sin = math.sin(rot_angle_rad)
            return Position2D(self.x + (position.x * rot_angle_rad_cos - position.y * rot_angle_rad_sin),
                              self.y + (position.y * rot_angle_rad_cos + position.x * rot_angle_rad_sin),
                              self.angle_deg)

    def rotate_by(self, angle_deg: float):
        if angle_deg == 0:
            return Position2D(self.x, self.y, self.angle_deg)
        else:
            rot_angle_rad = self.angle_rad
            rot_angle_rad_cos = math.cos(rot_angle_rad)
            rot_angle_rad_sin = math.sin(rot_angle_rad)
            return Position2D(self.x * rot_angle_rad_cos - self.y * rot_angle_rad_sin,
                              self.y * rot_angle_rad_cos + self.x * rot_angle_rad_sin,
                              self.angle_deg + angle_deg)

    def distance_to(self, position):
        return math.sqrt((self.x - position.x) ** 2 + (self.y - position.y) ** 2)

    def negative(self):
        return Position2D(-self.x, -self.y, -self.angle_deg)

        # TODO: add some support methods

    def generate_json_info(self):
        return {
            'x': self.x,
            'y': self.y,
            'angle_deg': self.angle_deg
        }
