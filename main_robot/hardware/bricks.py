from main_robot.hardware.brick_main import BRICK_MAIN
from main_robot.hardware.brick_scanner_distance import BRICK_SCANNER_DISTANCE_PROPULSION, \
    BRICK_SCANNER_DISTANCE_SENSOR, BRICK_SCANNER_DISTANCE
from main_robot.hardware.brick_scanner_reflect import BRICK_SCANNER_REFLECT_PROPULSION, \
    BRICK_SCANNER_REFLECT_SENSOR, BRICK_SCANNER_REFLECT
from main_robot.hardware.brick_wheel_left import BRICK_WHEEL_LEFT_PROPULSION, BRICK_WHEEL_LEFT
from main_robot.hardware.brick_wheel_right import BRICK_WHEEL_RIGHT_PROPULSION, BRICK_WHEEL_RIGHT

BRICKS = [
    BRICK_MAIN,

    BRICK_WHEEL_LEFT_PROPULSION, BRICK_WHEEL_LEFT,
    BRICK_WHEEL_RIGHT_PROPULSION, BRICK_WHEEL_RIGHT,

    BRICK_SCANNER_DISTANCE_PROPULSION, BRICK_SCANNER_DISTANCE_SENSOR, BRICK_SCANNER_DISTANCE,
    BRICK_SCANNER_REFLECT_PROPULSION, BRICK_SCANNER_REFLECT_SENSOR, BRICK_SCANNER_REFLECT
]
