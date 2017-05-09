from sumo_robot.hardware import hw_config as hwc
from utils.hardware.brick.base import ScannerBrick
from utils.hardware.brick.position import AbsoluteBrickPosition
from utils.hardware.brick.sensors import UltrasonicSensorBrick
from utils.hardware.sensor import SensorHeadDistanceMode

BRICK_SCANNER_DISTANCE_SENSOR = UltrasonicSensorBrick(AbsoluteBrickPosition(hwc.ScannerDistance.Head.pos_abs))

BRICK_SCANNER_DISTANCE = ScannerBrick(
    lambda distance_sensor: SensorHeadDistanceMode(None, distance_sensor), BRICK_SCANNER_DISTANCE_SENSOR,
    None, None
)
