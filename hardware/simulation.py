import sys

from utils.simulation.simulator import build_simulator
from .controller import CONTROLLER
from .devices_interfaces import DEVICES_INTERFACES

SIMULATION_MODE = '--simulate' in sys.argv or '-s' in sys.argv
SIM_ENV = build_simulator(CONTROLLER, *DEVICES_INTERFACES) if SIMULATION_MODE else None
