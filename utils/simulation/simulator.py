from utils.calc.position import Position2D

from utils.simulation.interface import DeviceInterface
from utils.simulation.world import World
from . import driver, interface


class SimulatedEnvironment:
    def __init__(self):
        self._drivers = []
        self._environment = {}

    @property
    def drivers(self):
        return self._drivers

    @property
    def environment(self):
        return self._environment

    def _add_device(self, device_interface: DeviceInterface, device: driver.DeviceDriver):
        class_name = device_interface.class_name
        if class_name not in self._environment:
            self._environment[class_name] = {}

        name = device_interface.name
        index = 0
        while name + str(index) in self._environment[class_name]:
            index += 1

        self._environment[class_name][name + str(index)] = device
        self._drivers.append(device)

    def create_device(self, world: World, device_interface: DeviceInterface):
        device = driver.DRIVERS[device_interface.driver_name](world, device_interface)
        self._add_device(device_interface, device)


def create_base_ev3_devices_interfaces(brick_center_position: Position2D):
    left_led_position = Position2D(-0.8, -1.5, 0) \
        .move_by(brick_center_position).rotate_by(brick_center_position.angle_deg)
    right_led_position = Position2D(0.8, -1.5, 0) \
        .move_by(brick_center_position).rotate_by(brick_center_position.angle_deg)
    return [
        interface.EV3LedInterface(left_led_position, 'ev3:left:red:ev3dev'),
        interface.EV3LedInterface(right_led_position, 'ev3:right:red:ev3dev'),
        interface.EV3LedInterface(left_led_position, 'ev3:left:green:ev3dev'),
        interface.EV3LedInterface(right_led_position, 'ev3:right:green:ev3dev')
    ]


def build_simulator(world: World, *devices_interfaces: DeviceInterface) -> SimulatedEnvironment:
    simulated_environment = SimulatedEnvironment()
    for device_interface in devices_interfaces:
        simulated_environment.create_device(world, device_interface)
    return simulated_environment
