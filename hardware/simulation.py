import sys

SIMULATION_MODE = '--simulate' in sys.argv
if SIMULATION_MODE:
    from utils.simulation.simulator import build_simulator
    from .robot import ROBOT_INFO
    from .world import WORLD

    SIM_ENV = build_simulator(WORLD, *ROBOT_INFO.devices_interfaces)
    WORLD.bind_simulated_environment(SIM_ENV)
else:
    SIM_ENV = None
