from main_robot.hardware import hw_config as hwc
from utils.hardware.brick.base import ScannerBrick
from utils.hardware.brick.motors import EV3MediumMotorBrick
from utils.hardware.brick.position import AbsoluteBrickPosition, RelativeBrickPosition
from utils.hardware.brick.sensors import InfraredSensorBrick
from utils.hardware.sensor import SensorHeadDistanceMode

BRICK_SCANNER_DISTANCE_PROPULSION = EV3MediumMotorBrick(AbsoluteBrickPosition(hwc.ScannerDistance.Propulsion.pos_abs))
BRICK_SCANNER_DISTANCE_PROPULSION.hw_position_range = hwc.ScannerDistance.Propulsion.position_range

BRICK_SCANNER_DISTANCE_SENSOR = InfraredSensorBrick(
    RelativeBrickPosition(hwc.ScannerDistance.Head.pos_rel, BRICK_SCANNER_DISTANCE_PROPULSION,
                          hwc.ScannerDistance.Head.gear_rotation, hwc.ScannerDistance.Propulsion.info.gear_ratio)
)

BRICK_SCANNER_DISTANCE = ScannerBrick(
    hwc.ScannerDistance.Propulsion.info, BRICK_SCANNER_DISTANCE_PROPULSION,
    lambda distance_sensor: SensorHeadDistanceMode(distance_sensor, None), BRICK_SCANNER_DISTANCE_SENSOR
)
