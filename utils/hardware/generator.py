from ev3dev.auto import Device

from utils.calc import dimensions as dp
from utils.control.pilot import Pilot
from utils.hardware.brick.base import Brick, ScannerBrick, WheelBrick
from utils.hardware.brick.bricks import Bricks
from utils.hardware.brick.main_brick import MainBrick
from utils.hardware.propulsion import ScannerPropulsion
from utils.hardware.simulation.brick_controller import BricksControllers
from utils.hardware.simulation.hardware import HW_MAP
from utils.hardware.simulation.robot_position_updater import RobotPositionUpdater
from utils.hardware.simulation.simulator import EnvironmentSimulator
from utils.hardware.simulation.world import World
from utils.hardware.simulation.world_map import WorldMap
from utils.hardware.wheel import Wheel
from utils.log import get_logger
from utils.sensor.scanner import Scanner

log = get_logger(__name__)


class HWControllerGenerator:
    def __init__(self, bricks: Bricks, environment_simulator: EnvironmentSimulator = None):
        self.bricks = bricks
        self.environment_simulator = environment_simulator

        self._hw_controllers = {}
        self._wheels = None
        self._pilot = None
        self._scanners = {}

    def hw_controller_for(self, brick, resolve_parent: bool = True) -> Device:
        if resolve_parent:
            brick = brick.resolve_parent()

        if brick in self._hw_controllers:
            return self._hw_controllers[brick]

        address = self.bricks.brick_port(brick)
        if address is None:
            raise Exception('Brick is not connected to robot.')

        if brick.hw_driver not in HW_MAP:
            raise Exception('Cannot find hw controller for brick.')

        hw_types = HW_MAP[brick.hw_driver]
        if self.environment_simulator is not None:
            hw_controller = hw_types[0](self.environment_simulator, address=address)
            log.info('Generating simulated HWController: ' +
                     str([hw_types[0].__name__, address, hw_controller.connected]))
        else:
            hw_controller = hw_types[1](address=address)
            log.info('Generating real HWController: ' +
                     str([hw_types[1].__name__, address, hw_controller.connected]))

        self._hw_controllers[brick] = hw_controller
        return hw_controller

    def wheels(self) -> tuple:
        if self._wheels is None:
            wheels_bricks = self.bricks.bricks_of_type(WheelBrick)
            self._wheels = tuple((
                Wheel(self.hw_controller_for(wheel_brick), wheel_brick.wheel_info)
                for wheel_brick in wheels_bricks
            ))
        return self._wheels

    def pilot(self) -> Pilot:
        if self._pilot is None:
            self._pilot = Pilot(*self.wheels())
        return self._pilot

    def scanner(self, scanner_brick: ScannerBrick) -> Scanner:
        if scanner_brick in self._scanners:
            return self._scanners[scanner_brick]

        propulsion = ScannerPropulsion(self.hw_controller_for(scanner_brick.propulsion_brick),
                                       scanner_brick.propulsion_info)
        head = scanner_brick.scanner_head_mode_creator(self.hw_controller_for(scanner_brick.head_brick))
        scanner = Scanner(propulsion, head)
        self._scanners[scanner_brick] = scanner
        return scanner

    def generate_json_info(self):
        return {
            'bricks': self.bricks.generate_json_info(),
            'environment_simulator': self.environment_simulator.generate_json_info()
            if self.environment_simulator is not None else None
        }


def log_bricks_info(bricks: Bricks, bricks_controllers: BricksControllers = None):
    log.info('BricksInfo:')
    for brick in bricks.tuple_bricks:
        brick_type = type(brick)
        address = bricks.brick_port(brick)
        position = brick.position.get(bricks_controllers)
        log.info('--Type: ' + str(brick_type.__name__) + ', Address: ' + str(address) + ',  Position: ' + str(position))


def build_simulated(world_map: WorldMap, main_brick: MainBrick, *bricks: Brick,
                    robot_position: dp.Position = None, **ports: Brick) -> HWControllerGenerator:
    log.info('Building simulated HWController...')
    if robot_position is None:
        robot_position = dp.Position(dp.Point(world_map.width / 2, world_map.height / 2, 0), dp.Angle())
    bricks = Bricks(main_brick, *bricks, **ports)
    world = World(robot_position, world_map)
    bricks_controllers = BricksControllers(world, bricks)
    robot_position_updater = RobotPositionUpdater(bricks, bricks_controllers, robot_position)
    env_simulator = EnvironmentSimulator(bricks_controllers, robot_position_updater)
    log_bricks_info(bricks, bricks_controllers)
    return HWControllerGenerator(bricks, env_simulator)


def build_real(main_brick: MainBrick, *bricks: Brick, **ports: Brick) -> HWControllerGenerator:
    log.info('Building real HWController...')
    bricks = Bricks(main_brick, *bricks, **ports)
    log_bricks_info(bricks)
    return HWControllerGenerator(bricks, None)
