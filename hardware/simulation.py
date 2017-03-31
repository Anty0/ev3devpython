import sys

from utils.simulation.simulator import build_simulator
from .controller import CONTROLLER
from .robot import ROBOT_INFO

SIMULATION_MODE = '--simulate' in sys.argv or '-s' in sys.argv
SIM_ENV = build_simulator(CONTROLLER, *ROBOT_INFO.devices_interfaces) if SIMULATION_MODE else None
