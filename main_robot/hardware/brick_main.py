from main_robot.hardware import hw_config as hwc
from utils.hardware.brick.main_brick import MainEV3Brick
from utils.hardware.brick.position import AbsoluteBrickPosition

BRICK_MAIN = MainEV3Brick(AbsoluteBrickPosition(hwc.MainBrick.pos_abs))
