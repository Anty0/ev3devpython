from  hardware import hw_config as hwc
from hardware.brick_scanner_distance import BRICK_SCANNER_DISTANCE_PROPULSION, BRICK_SCANNER_DISTANCE_SENSOR
from hardware.brick_scanner_reflect import BRICK_SCANNER_REFLECT_PROPULSION, BRICK_SCANNER_REFLECT_SENSOR
from hardware.brick_wheel_left import BRICK_WHEEL_LEFT_PROPULSION
from hardware.brick_wheel_right import BRICK_WHEEL_RIGHT_PROPULSION

PORTS = {
    hwc.WheelLeft.Propulsion.port: BRICK_WHEEL_LEFT_PROPULSION,
    hwc.WheelRight.Propulsion.port: BRICK_WHEEL_RIGHT_PROPULSION,

    hwc.ScannerDistance.Propulsion.port: BRICK_SCANNER_DISTANCE_PROPULSION,
    hwc.ScannerDistance.Head.port: BRICK_SCANNER_DISTANCE_SENSOR,

    hwc.ScannerReflect.Propulsion.port: BRICK_SCANNER_REFLECT_PROPULSION,
    hwc.ScannerReflect.Head.port: BRICK_SCANNER_REFLECT_SENSOR
}
