from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread, Event

from utils.web.api_http_handler import ApiHTTPRequestHandler
from .log import get_logger

log = get_logger(__name__)


class Program:
    SERVER_PORT = 8000

    def __init__(self, request_handler_class: BaseHTTPRequestHandler = ApiHTTPRequestHandler):
        self._server = HTTPServer(('', self.SERVER_PORT), request_handler_class)
        self._running = False
        self._stop_event = Event()
        self._stop_event.set()

    def _on_start(self):
        pass

    def _on_exit(self):
        pass

    def is_running(self):
        return self._running

    def can_start(self):
        return not self.is_running()

    def wait_to_exit(self):
        self._stop_event.wait()

    def start(self):
        if not self.can_start():
            return False

        self._stop_event.clear()
        self._running = True

        def run_server():
            try:
                self._on_start()
                self._server.serve_forever()
            except (KeyboardInterrupt, Exception) as e:
                log.exception(e)
                self._server.shutdown()
            finally:
                self._on_exit()
                self._running = False
                self._stop_event.set()

        Thread(target=run_server).start()
        log.info("Started HTTP server on port %d" % self.SERVER_PORT)
        return True

    def exit(self):
        if self._running:
            self._server.shutdown()

    def __del__(self):
        self._server.server_close()
