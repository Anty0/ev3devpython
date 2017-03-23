from ev3dev.auto import MediumMotor

from utils.hardware.propulsion import ScannerPropulsion
from utils.hardware.sensor import SensorHeadReflectMode
from utils.sensor.scanner import Scanner
from utils.simulation.hardware import SimMediumMotor
from .brick import BRICK
from .hw_config import SCANNER_REFLECT_PROPULSION_PORT, SCANNER_REFLECT_PROPULSION_GEAR_RATIO
from .sensor_color import SENSOR_COLOR

if BRICK.sim_env is not None:
    SCANNER_REFLECT_PROPULSION_MOTOR = SimMediumMotor(BRICK.sim_env, SCANNER_REFLECT_PROPULSION_PORT)
else:
    SCANNER_REFLECT_PROPULSION_MOTOR = MediumMotor(SCANNER_REFLECT_PROPULSION_PORT)

SCANNER_REFLECT_PROPULSION = ScannerPropulsion(SCANNER_REFLECT_PROPULSION_MOTOR, SCANNER_REFLECT_PROPULSION_GEAR_RATIO)
SCANNER_REFLECT_HEAD = SensorHeadReflectMode(SENSOR_COLOR)
SCANNER_REFLECT = Scanner(SCANNER_REFLECT_PROPULSION, SCANNER_REFLECT_HEAD)
