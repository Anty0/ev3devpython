from ev3dev.auto import MediumMotor

from utils.hardware.propulsion import ScannerPropulsion
from utils.hardware.sensor import SensorHeadDistanceMode
from utils.sensor.scanner import Scanner
from utils.simulation.hardware import SimMediumMotor
from .brick import BRICK
from .hw_config import SCANNER_DISTANCE_PROPULSION_PORT, SCANNER_DISTANCE_PROPULSION_GEAR_RATIO
from .sensor_infrared import SENSOR_INFRARED
from .sensor_ultrasonic import SENSOR_ULTRASONIC

if BRICK.sim_env is not None:
    SCANNER_DISTANCE_PROPULSION_MOTOR = SimMediumMotor(BRICK.sim_env, SCANNER_DISTANCE_PROPULSION_PORT)
else:
    SCANNER_DISTANCE_PROPULSION_MOTOR = MediumMotor(SCANNER_DISTANCE_PROPULSION_PORT)

SCANNER_DISTANCE_PROPULSION = ScannerPropulsion(SCANNER_DISTANCE_PROPULSION_MOTOR,
                                                SCANNER_DISTANCE_PROPULSION_GEAR_RATIO)
SCANNER_DISTANCE_HEAD = SensorHeadDistanceMode(SENSOR_INFRARED, SENSOR_ULTRASONIC)
SCANNER_REFLECT = Scanner(SCANNER_DISTANCE_PROPULSION, SCANNER_DISTANCE_HEAD)
