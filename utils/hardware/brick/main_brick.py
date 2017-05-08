from utils.calc.color import COL_LIGHT_GRAY, COL_DARK_GRAY
from utils.hardware.brick.base import Brick
from utils.hardware.brick.position import BrickPosition


class MainBrick(Brick):
    def __init__(self, position: BrickPosition):
        super().__init__(position)

    pass  # TODO: Add some info about brick


class MainEV3Brick(MainBrick):
    def __init__(self, position: BrickPosition):
        super().__init__(position)
        self.size = None  # TODO: find on web
        self.color = COL_LIGHT_GRAY

    # TODO: provides two leds (controller will auto create two drivers for this brick)
    pass  # TODO: Add some info about brick


class MainRPI1Brick(MainBrick):
    def __init__(self, position: BrickPosition):
        super().__init__(position)
        self.size = None  # TODO: find on web
        self.color = COL_DARK_GRAY

    pass  # TODO: Add some info about brick


class MainRPI2Brick(MainBrick):
    def __init__(self, position: BrickPosition):
        super().__init__(position)
        self.size = None  # TODO: find on web
        self.color = COL_DARK_GRAY

    pass  # TODO: Add some info about brick
