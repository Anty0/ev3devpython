import sys

from utils.simulation.simulator import build_simulator
from .robot import ROBOT_INFO
from .world import WORLD

SIMULATION_MODE = '--simulate' in sys.argv
SIM_ENV = build_simulator(WORLD, *ROBOT_INFO.devices_interfaces) if SIMULATION_MODE else None
