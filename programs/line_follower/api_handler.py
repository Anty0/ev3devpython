from threading import Lock

from programs.line_follower.thread_collision_avoid import run_loop as run_loop_collision_avoid
from utils.program import ProgramApiHandler
from utils.threading.co_working_threads import ThreadsController
from .config import THREAD_LINE_FOLLOW_NAME, THREAD_COLLISION_AVOID_NAME
from .shared_data import LineFollowerSharedData as SharedData
from .thread_line_follow import run_loop as run_loop_line_follow


class Target:
    def __init__(self):
        self.shared_data = SharedData()
        self.controller = ThreadsController(self.shared_data, **{
            THREAD_LINE_FOLLOW_NAME: run_loop_line_follow,
            THREAD_COLLISION_AVOID_NAME: run_loop_collision_avoid
        })


class LineFollowerApiRequestHandler(ProgramApiHandler):
    _lock = Lock()
    _target = None

    @staticmethod
    def start_controller(config: dict = None):
        self = LineFollowerApiRequestHandler
        with self._lock:
            if self._target is None:
                self._target = Target()
            self._target.shared_data.config.update_config(config)
            self._target.shared_data.reset()
            self._target.controller.start()

    @staticmethod
    def destroy_controller():
        self = LineFollowerApiRequestHandler
        with self._lock:
            if self._target is not None:
                self._target.controller.stop()
                self._target.controller.wait_to_stop()
                self._target.shared_data.reset()

    def get_config(self):
        return self._target.shared_data.config.extract_config_values()

    def update_config(self, config: dict):
        self._target.shared_data.config.update_config(config)

    def get_api_actions(self):
        return {'Perform line scan': 'perform_line_scan'}

    def action_perform_line_scan(self):
        self._target.shared_data.data.perform_line_scan = True

    def is_paused(self):
        return self._target.shared_data.pause

    def resume(self):
        self._target.shared_data.pause = False

    def pause(self):
        self._target.shared_data.pause = True

    def get_new_graphs(self):
        return self._target.shared_data.get_new_graphs()

    def get_hw_info(self):
        return self._target.shared_data.generate_json_info()
