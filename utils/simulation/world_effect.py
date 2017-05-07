from utils.calc.position import Position2D

from utils.calc.size import Size
from utils.hardware.wheel import WheelInfo
from utils.simulation.driver import DeviceDriver


class WorldEffect:
    def __init__(self, position: Position2D, size: Size):
        self.position = position
        self.size = size

    def draw(self, world, driver: DeviceDriver, canvas):
        pass  # TODO: draw black square


class WheelEffect(WorldEffect):
    def __init__(self, wheel_info: WheelInfo):
        super().__init__(wheel_info.position, wheel_info.size)
        self.wheel_info = wheel_info

    def draw(self, world, driver: DeviceDriver, canvas):
        pass  # TODO: draw wheel


class LedEffect(WorldEffect):
    def __init__(self, position: Position2D):
        super().__init__(position, Size(1, 1, 1, 1))  # TODO: measure

    def draw(self, world, driver: DeviceDriver, canvas):
        pass  # TODO: draw led
