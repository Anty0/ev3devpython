from utils.simulation.interface import EV3LargeMotorInterface, EV3MediumMotorInterface, \
    EV3ColorSensorInterface, EV3InfraredSensorInterface
from utils.simulation.simulator import get_base_ev3_devices
from .hw_config import WHEEL_MOTOR_LEFT_PORT, WHEEL_MOTOR_LEFT_POSITION, \
    WHEEL_MOTOR_RIGHT_PORT, WHEEL_MOTOR_RIGHT_POSITION, \
    SCANNER_DISTANCE_PROPULSION_PORT, SCANNER_DISTANCE_PROPULSION_POSITION, \
    SCANNER_REFLECT_PROPULSION_PORT, SCANNER_REFLECT_PROPULSION_POSITION, \
    SCANNER_DISTANCE_HEAD_PORT, SCANNER_DISTANCE_HEAD_POSITION, \
    SCANNER_REFLECT_HEAD_PORT, SCANNER_REFLECT_HEAD_POSITION, \
    BRICK_POSITION

DEVICES_INTERFACES = [
                         EV3LargeMotorInterface(WHEEL_MOTOR_LEFT_POSITION, WHEEL_MOTOR_LEFT_PORT),
                         EV3LargeMotorInterface(WHEEL_MOTOR_RIGHT_POSITION, WHEEL_MOTOR_RIGHT_PORT),
                         EV3MediumMotorInterface(SCANNER_DISTANCE_PROPULSION_POSITION,
                                                 SCANNER_DISTANCE_PROPULSION_PORT),
                         EV3MediumMotorInterface(SCANNER_REFLECT_PROPULSION_POSITION,
                                                 SCANNER_REFLECT_PROPULSION_PORT),
                         EV3InfraredSensorInterface(SCANNER_DISTANCE_HEAD_POSITION, SCANNER_DISTANCE_HEAD_PORT),
                         EV3ColorSensorInterface(SCANNER_REFLECT_HEAD_POSITION, SCANNER_REFLECT_HEAD_PORT)
                     ] + get_base_ev3_devices(BRICK_POSITION)
