from sumo_robot.hardware import hw_config as hwc
from sumo_robot.hardware.brick_scanner_distance import BRICK_SCANNER_DISTANCE_SENSOR
from sumo_robot.hardware.brick_wheel_left import BRICK_WHEEL_LEFT_PROPULSION
from sumo_robot.hardware.brick_wheel_right import BRICK_WHEEL_RIGHT_PROPULSION

PORTS = {
    hwc.WheelLeft.Propulsion.port: BRICK_WHEEL_LEFT_PROPULSION,
    hwc.WheelRight.Propulsion.port: BRICK_WHEEL_RIGHT_PROPULSION,

    hwc.ScannerDistance.Head.port: BRICK_SCANNER_DISTANCE_SENSOR
}
