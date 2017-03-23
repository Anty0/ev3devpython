from utils.calc.position import Position2D
from utils.simulation.simulator import SimulatedEnvironment


class Brick:
    def __init__(self, position: Position2D = None,
                 simulated_environment: SimulatedEnvironment = None):
        self._position = position if position is not None else Position2D(0, 0, 0)
        self._simulated_environment = simulated_environment

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    @property
    def sim_env(self):
        return self._simulated_environment
