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

    def offset_by(self, offset_position):  # TODO: if self.angle != 0 offset x and y by rotated offset
        return Position2D(self.x + offset_position.x,
                          self.y + offset_position.y,
                          self.angle_deg + offset_position.angle_deg)

    def offset_by_raw(self, x: float, y: float, angle_deg: float):
        # TODO: if self.angle != 0 offset x and y by rotated offset
        return Position2D(self.x + x, self.y + y,
                          self.angle_deg + angle_deg)

    def distance_to(self, position):
        return math.sqrt((self.x - position.x) ** 2 + (self.y - position.y) ** 2)

        # TODO: add some basic calculations support methods

    def negative(self):
        return Position2D(-self.x, -self.y, -self.angle_deg)

    def generate_json_info(self):
        return {
            'x': self.x,
            'y': self.y,
            'angle_deg': self.angle_deg
        }
