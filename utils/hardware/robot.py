from utils.calc.position import Position2D

from utils.calc.size import Size


class Robot:
    def __init__(self, size: Size, *devices_interfaces: list,
                 position: Position2D = None):
        self._size = size
        self._devices_interfaces = devices_interfaces
        self._position = position if position is not None else Position2D(0, 0, 0)

    @property
    def size(self):
        return self._size

    @property
    def devices_interfaces(self):
        return self._devices_interfaces

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value
