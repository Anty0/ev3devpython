from utils.program import Program
from .api_handler import LineFollowerApiRequestHandler as ApiRequestHandler


class LineFollowProgram(Program):
    def __init__(self):
        super().__init__(request_handler_class=ApiRequestHandler)

    def _on_start(self, config: dict = None):
        ApiRequestHandler.start_controller(config)

    def _on_exit(self):
        ApiRequestHandler.destroy_controller()
