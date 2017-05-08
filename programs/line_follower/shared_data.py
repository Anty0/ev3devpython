from threading import Lock

from utils.debug_mode import DEBUG_MODE
from utils.program import graph_obj_to_string
from utils.runtime_config import RuntimeConfig
from .config import CONFIG_VALUES


class LineFollowerSharedData:
    def __init__(self, config: dict = None):
        from hardware.hw_config import Robot
        from hardware.generator import HW_GENERATOR
        from hardware.brick_scanner_reflect import BRICK_SCANNER_REFLECT
        from hardware.brick_scanner_distance import BRICK_SCANNER_DISTANCE

        self.robot_size = Robot.size
        self.pilot = HW_GENERATOR.pilot()
        self.scanner_reflect = HW_GENERATOR.scanner(BRICK_SCANNER_REFLECT)
        self.scanner_distance = HW_GENERATOR.scanner(BRICK_SCANNER_DISTANCE)

        if not self.pilot.is_connected or not self.scanner_reflect.head_connected:
            raise Exception('LineFollower requires wheels and color sensor at last.')

        self.config = RuntimeConfig(config_map=CONFIG_VALUES, config_modifications=config)

        self.line_info = {
            'max_position': 0,
            'position_offset': 0,
            'min_reflect': 0,
            'max_reflect': 100,
            'reflect_to_position_list': [0] * 101,
        }

        self.pause = DEBUG_MODE
        self.perform_line_scan = True

        self._graphs_lock = Lock()
        self._graphs = []

    def add_new_graph(self, graph: dict):
        with self._graphs_lock:
            self._graphs.append(graph)
        print(graph_obj_to_string(graph))

    def get_new_graphs(self) -> list:
        with self._graphs_lock:
            new_graphs = self._graphs
            self._graphs = []

        return new_graphs

    def reset(self):
        self.pilot.reset()
        self.scanner_reflect.reset()
        self.scanner_distance.reset()
        self.pause = True

    def generate_json_info(self):
        return {
            'pause': self.pause,
            'robot_size': self.robot_size.generate_json_info(),
            'pilot': self.pilot.generate_json_info(),
            'scanner_reflect': self.scanner_reflect.generate_json_info(),
            'scanner_distance': self.scanner_distance.generate_json_info(),
            'config': self.config.generate_json_info(),
        }
