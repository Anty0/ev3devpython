from utils.calc.color import COL_GRAY
from utils.calc.size import Size
from utils.hardware.brick.base import MotorBrick, ActiveBrick
from utils.hardware.brick.position import BrickPosition


# TODO: implement draw method for each MotorBrick


class EV3LargeMotorBrick(MotorBrick):
    def __init__(self, position: BrickPosition):
        super().__init__(position)
        self.offset_center = None  # TODO: find on web
        self.size = Size(1, 1, 1, 0)  # TODO: find on web
        self.color = COL_GRAY

        self.hw_driver = 'lego-ev3-l-motor'
        self.hw_commands = self.ALL_COMMANDS
        self.hw_count_per_rot = 360
        self.hw_max_speed = 1050


class NXTLargeMotorBrick(MotorBrick):
    def __init__(self, position: BrickPosition):
        super().__init__(position)
        self.offset_center = None  # TODO: find on web
        self.size = Size(1, 1, 1, 0)  # TODO: find on web
        self.color = COL_GRAY

        self.hw_driver = 'lego-nxt-motor'
        self.hw_commands = self.ALL_COMMANDS
        self.hw_count_per_rot = 360
        self.hw_max_speed = 1050


class EV3MediumMotorBrick(MotorBrick):
    def __init__(self, position: BrickPosition):
        super().__init__(position)
        self.offset_center = None  # TODO: find on web
        self.size = Size(1, 1, 1, 0)  # TODO: find on web
        self.color = COL_GRAY

        self.hw_driver = 'lego-ev3-m-motor'
        self.hw_commands = self.ALL_COMMANDS
        self.hw_count_per_rot = 360
        self.hw_max_speed = 1050  # TODO: extract defaults from robot


class ActuonixL1250MotorBrick(MotorBrick):  # placeholder
    pass  # TODO: add support


class ActuonixL12100MotorBrick(MotorBrick):  # placeholder
    pass  # TODO: add support


class DcMotorBrick(ActiveBrick):  # placeholder
    pass  # TODO: add support


class ServoMotorBrick(ActiveBrick):  # placeholder
    pass  # TODO: add support
