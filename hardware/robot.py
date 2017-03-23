from utils.calc.size import Size
from utils.hardware.robot import Robot
from .hw_config import ROBOT_WIDTH, ROBOT_LENGTH, ROBOT_HEIGHT, ROBOT_WEIGHT

ROBOT_INFO = Robot(Size(ROBOT_WIDTH, ROBOT_LENGTH, ROBOT_HEIGHT, ROBOT_WEIGHT))
