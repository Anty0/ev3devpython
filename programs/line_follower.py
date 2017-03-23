import time
from threading import Thread, Event

from utils.program import Program
from utils.web.api_http_handler import ApiHTTPRequestHandler

CONTROLLER = None


class RuntimeController(Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self._run = True
        self._stop_event = Event()

    def stop(self):
        self._run = False

    def wait_to_stop(self):
        self._stop_event.wait()

    def run(self):
        try:
            while self._run:
                time.sleep(0.5)
        finally:
            self._stop_event.set()


class RequestHandler(ApiHTTPRequestHandler):
    def get_api_dict(self):
        return super().get_api_dict()  # TODO: implement


class LineFollowProgram(Program):
    def __init__(self):
        super().__init__(request_handler_class=RequestHandler)

    def can_start(self):
        return super().can_start() and CONTROLLER is None

    def _on_start(self):
        global CONTROLLER
        CONTROLLER = RuntimeController()
        CONTROLLER.start()

    def _on_exit(self):
        global CONTROLLER
        CONTROLLER.stop()
        CONTROLLER.wait_to_stop()
        CONTROLLER = None
