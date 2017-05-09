from sumo_robot.hardware.brick_main import BRICK_MAIN
from sumo_robot.hardware.brick_scanner_distance import BRICK_SCANNER_DISTANCE_SENSOR, BRICK_SCANNER_DISTANCE
from sumo_robot.hardware.brick_wheel_left import BRICK_WHEEL_LEFT_PROPULSION, BRICK_WHEEL_LEFT
from sumo_robot.hardware.brick_wheel_right import BRICK_WHEEL_RIGHT_PROPULSION, BRICK_WHEEL_RIGHT

BRICKS = [
    BRICK_MAIN,

    BRICK_WHEEL_LEFT_PROPULSION, BRICK_WHEEL_LEFT,
    BRICK_WHEEL_RIGHT_PROPULSION, BRICK_WHEEL_RIGHT,

    BRICK_SCANNER_DISTANCE_SENSOR, BRICK_SCANNER_DISTANCE
]
