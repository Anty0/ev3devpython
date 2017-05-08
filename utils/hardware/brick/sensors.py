from utils.calc.color import COL_GRAY, COL_DARK_GRAY
from utils.calc.size import Size
from utils.hardware.brick.base import SensorBrick
from utils.hardware.brick.position import BrickPosition


# TODO: implement draw method for each SensorBrick


class TouchSensorBrick(SensorBrick):
    def __init__(self, position: BrickPosition):
        super().__init__(position)


class EV3TouchSensorBrick(TouchSensorBrick):
    def __init__(self, position: BrickPosition):
        super().__init__(position)
        self.size = Size(1, 1, 1, 0)  # TODO: find on web
        self.color = COL_GRAY

        self.hw_driver = 'lego-ev3-touch'


class NXTTouchSensorBrick(TouchSensorBrick):
    def __init__(self, position: BrickPosition):
        super().__init__(position)
        self.size = Size(1, 1, 1, 0)  # TODO: find on web
        self.color = COL_DARK_GRAY

        self.hw_driver = 'lego-nxt-touch'


class ColorSensorBrick(SensorBrick):
    def __init__(self, position: BrickPosition):
        super().__init__(position)


class EV3ColorSensorBrick(ColorSensorBrick):
    def __init__(self, position: BrickPosition):
        super().__init__(position)
        self.size = Size(1, 1, 1, 0)  # TODO: find on web
        self.color = COL_GRAY

        self.hw_driver = 'lego-ev3-color'


class UltrasonicSensorBrick(SensorBrick):
    def __init__(self, position: BrickPosition):
        super().__init__(position)


class EV3UltrasonicSensorBrick(UltrasonicSensorBrick):
    def __init__(self, position: BrickPosition):
        super().__init__(position)
        self.size = Size(1, 1, 1, 0)  # TODO: find on web
        self.color = COL_DARK_GRAY

        self.hw_driver = 'lego-ev3-us'


class NXTUltrasonicSensorBrick(UltrasonicSensorBrick):
    def __init__(self, position: BrickPosition):
        super().__init__(position)
        self.size = Size(1, 1, 1, 0)  # TODO: find on web
        self.color = COL_DARK_GRAY

        self.hw_driver = 'lego-nxt-us'


class GyroSensorBrick(SensorBrick):
    def __init__(self, position: BrickPosition):
        super().__init__(position)


class EV3GyroSensorBrick(GyroSensorBrick):
    def __init__(self, position: BrickPosition):
        super().__init__(position)
        self.size = Size(1, 1, 1, 0)  # TODO: find on web
        self.color = COL_GRAY

        self.hw_driver = 'lego-ev3-gyro'


class InfraredSensorBrick(SensorBrick):
    def __init__(self, position: BrickPosition):
        super().__init__(position)


class EV3InfraredSensorBrick(InfraredSensorBrick):
    def __init__(self, position: BrickPosition):
        super().__init__(position)
        self.size = Size(1, 1, 1, 0)  # TODO: find on web
        self.color = COL_DARK_GRAY

        self.hw_driver = 'lego-ev3-ir'


class SoundSensorBrick(SensorBrick):
    def __init__(self, position: BrickPosition):
        super().__init__(position)


class NXTSoundSensorBrick(SoundSensorBrick):
    def __init__(self, position: BrickPosition):
        super().__init__(position)
        self.size = Size(1, 1, 1, 0)  # TODO: find on web
        self.color = COL_GRAY

        self.hw_driver = 'lego-nxt-sound'


class LightSensorBrick(SensorBrick):
    def __init__(self, position: BrickPosition):
        super().__init__(position)


class NXTLightSensorBrick(SoundSensorBrick):
    def __init__(self, position: BrickPosition):
        super().__init__(position)
        self.size = Size(1, 1, 1, 0)  # TODO: find on web
        self.color = COL_GRAY

        self.hw_driver = 'lego-nxt-light'
