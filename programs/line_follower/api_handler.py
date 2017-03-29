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
            self._target.controller.stop()
            self._target.controller.wait_to_stop()
            self._target.shared_data.reset()

    def get_config(self):
        return super().get_config()

    def update_config(self, config: dict):
        return super().update_config(config)

    def get_api_actions(self):
        return super().get_api_actions()
