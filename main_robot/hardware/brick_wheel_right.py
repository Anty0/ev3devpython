from main_robot.hardware import hw_config as hwc
from utils.hardware.brick.base import WheelBrick
from utils.hardware.brick.motors import EV3LargeMotorBrick
from utils.hardware.brick.position import AbsoluteBrickPosition

BRICK_WHEEL_RIGHT_PROPULSION = EV3LargeMotorBrick(AbsoluteBrickPosition(hwc.WheelRight.Propulsion.pos_abs))
BRICK_WHEEL_RIGHT = WheelBrick(BRICK_WHEEL_RIGHT_PROPULSION, hwc.WheelRight.info)
