import math
import time
from threading import Thread

from utils.hardware.robot import Robot
from utils.utils import wait_to_cycle_time


# class RobotInfo:
#     def __init__(self, *devices_interfaces: list):
#         self._prepared = False
#         self._devices = []
#         for devices_interface in devices_interfaces:
#             self._devices.append({'interface': devices_interface, 'device': None})
#
#         self._wheels = []
#         self._sensors = []
#         self._leds = []
#
#     @property
#     def is_prepared(self):
#         return self._prepared
#
#     def prepare_devices(self, sim_environment=None):
#         self._wheels.clear()
#         self._sensors.clear()
#         self._leds.clear()
#
#         for device_info in self._devices:
#             interface = device_info['interface']
#             device = None
#             # TODO: implement
#             device_info['device'] = device
#
#         self._prepared = True
#
#     @property
#     def devices(self):
#         return self._devices
#
#     @property
#     def wheels(self):
#         return self._wheels
#
#     @property
#     def sensors(self):
#         return self._sensors
#
#     @property
#     def leds(self):
#         return self._leds


class World:
    def __init__(self, robot: Robot):
        self._robot = robot
        self._map = None  # TODO: create
        self._odometry = None

    @property
    def robot(self):
        return self._robot

    # def prepare_devices(self, sim_environment=None):
    #     # self.robot.prepare_devices(sim_environment)
    #     self._start_odometry()

    def _start_odometry(self):
        if self._odometry is None:
            self._odometry = Thread(target=self._run_odometry, name='OdometryThread', daemon=True)
            # self._odometry.start()

    def _run_odometry(self):
        cycle_time = 0.1
        last_time = time.time()
        while True:
            # TODO: implement and allow starting
            last_time = wait_to_cycle_time('Odometry', last_time, cycle_time)
        pass

    def get_map(self):
        return self._map

    def set_actual_pos(self, position):
        self._position = position

    def get_actual_pos(self):
        return self._position

    def get_color_rgb_on_pos(self, offset_position=None):
        return [0, 0, 0]  # TODO: implement

    def get_reflect_on_pos(self, offset_position=None):
        return 50  # TODO: implement

    def get_light_on_pos(self, offset_position=None):
        return 50  # TODO: implement

    def get_distance_on_pos(self, offset_position=None):
        return math.inf  # TODO: implement

    def get_beacon_pos_offset(self, offset_position=None):
        return None  # TODO: implement

    def is_pos_in_wall(self, offset_position=None):
        return False  # TODO: implement

    def get_noise_on_pos(self, offset_position=None, use_a_weighting=False):
        return 0  # TODO: implement
