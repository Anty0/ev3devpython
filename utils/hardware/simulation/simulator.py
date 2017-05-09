from utils.hardware.simulation.brick_controller import BricksControllers
from utils.hardware.simulation.driver import DRIVERS_MAP, DeviceDriver
from utils.hardware.simulation.robot_position_updater import RobotPositionUpdater


class EnvironmentSimulator:
    def __init__(self, bricks_controllers: BricksControllers, robot_position_updater: RobotPositionUpdater):
        self.bricks_controllers = bricks_controllers
        self.robot_position_updater = robot_position_updater

        self.environment = {}
        self._drivers = {}

        for port, brick in self.bricks_controllers.bricks.ports.items():
            if brick is not None:
                self.driver(brick)

    def driver(self, brick, resolve_parent: bool = True) -> DeviceDriver:
        if resolve_parent:
            brick = brick.resolve_parent()

        if brick in self._drivers:
            return self._drivers[brick]

        class_name = brick.hw_class
        if class_name not in self.environment:
            self.environment[class_name] = {}

        name = brick.hw_id
        index = 0
        while name + str(index) in self.environment[class_name]:
            index += 1

        brick_controller = self.bricks_controllers.brick_controller(brick, resolve_parent=False)
        driver = DRIVERS_MAP[brick.hw_driver](self.bricks_controllers.bricks, brick_controller)
        self.environment[class_name][name + str(index)] = driver
        self._drivers[brick] = driver
        return driver

    def generate_json_info(self):
        return {}  # TODO: implement
