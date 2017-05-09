from main_robot.hardware import hw_config as hwc
from utils.hardware.brick.base import ScannerBrick
from utils.hardware.brick.motors import EV3MediumMotorBrick
from utils.hardware.brick.position import AbsoluteBrickPosition, RelativeBrickPosition
from utils.hardware.brick.sensors import ColorSensorBrick
from utils.hardware.sensor import SensorHeadReflectMode

BRICK_SCANNER_REFLECT_PROPULSION = EV3MediumMotorBrick(AbsoluteBrickPosition(hwc.ScannerReflect.Propulsion.pos_abs))
BRICK_SCANNER_REFLECT_PROPULSION.hw_position_range = hwc.ScannerReflect.Propulsion.position_range

BRICK_SCANNER_REFLECT_SENSOR = ColorSensorBrick(
    RelativeBrickPosition(hwc.ScannerReflect.Head.pos_rel, BRICK_SCANNER_REFLECT_PROPULSION,
                          hwc.ScannerReflect.Head.gear_rotation, hwc.ScannerReflect.Propulsion.info.gear_ratio)
)

BRICK_SCANNER_REFLECT = ScannerBrick(
    hwc.ScannerReflect.Propulsion.info, BRICK_SCANNER_REFLECT_PROPULSION,
    lambda color_sensor: SensorHeadReflectMode(color_sensor), BRICK_SCANNER_REFLECT_SENSOR
)
