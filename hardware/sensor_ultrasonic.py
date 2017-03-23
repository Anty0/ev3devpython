from ev3dev.auto import UltrasonicSensor

from utils.simulation.hardware import SimUltrasonicSensor
from .brick import BRICK
from .hw_config import SCANNER_DISTANCE_HEAD_PORT

if BRICK.sim_env is not None:
    SENSOR_ULTRASONIC = SimUltrasonicSensor(BRICK.sim_env, SCANNER_DISTANCE_HEAD_PORT)
else:
    SENSOR_ULTRASONIC = UltrasonicSensor(SCANNER_DISTANCE_HEAD_PORT)
