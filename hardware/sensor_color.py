from ev3dev.auto import ColorSensor

from utils.simulation.hardware import SimColorSensor
from .brick import BRICK
from .hw_config import SCANNER_REFLECT_HEAD_PORT

if BRICK.sim_env is not None:
    SENSOR_COLOR = SimColorSensor(BRICK.sim_env, SCANNER_REFLECT_HEAD_PORT)
else:
    SENSOR_COLOR = ColorSensor(SCANNER_REFLECT_HEAD_PORT)
