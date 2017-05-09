from sumo_robot.hardware import hw_config as hwc
from utils.hardware.brick.base import WheelBrick
from utils.hardware.brick.motors import EV3LargeMotorBrick
from utils.hardware.brick.position import AbsoluteBrickPosition

BRICK_WHEEL_LEFT_PROPULSION = EV3LargeMotorBrick(AbsoluteBrickPosition(hwc.WheelLeft.Propulsion.pos_abs))
BRICK_WHEEL_LEFT = WheelBrick(BRICK_WHEEL_LEFT_PROPULSION, hwc.WheelLeft.info)
