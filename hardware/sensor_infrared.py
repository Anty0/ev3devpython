from ev3dev.auto import InfraredSensor

from utils.simulation.hardware import SimInfraredSensor
from .brick import BRICK
from .hw_config import SCANNER_DISTANCE_HEAD_PORT

if BRICK.sim_env is not None:
    SENSOR_INFRARED = SimInfraredSensor(BRICK.sim_env, SCANNER_DISTANCE_HEAD_PORT)
else:
    SENSOR_INFRARED = InfraredSensor(SCANNER_DISTANCE_HEAD_PORT)
