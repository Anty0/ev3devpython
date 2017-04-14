import json
from http.server import HTTPServer
from threading import Thread, Event

from utils.calc.range import Range
from utils.debug_mode import DEBUG_MODE
from utils.graph import graph_to_string, GraphPoint
from utils.web.api_http_handler import ApiHTTPRequestHandler
from .log import get_logger, add_logging_listener

log = get_logger(__name__)
LOG_CHANGES = ''

if DEBUG_MODE:
    def _add_to_log_changes(msg):
        global LOG_CHANGES
        LOG_CHANGES += msg


    add_logging_listener(_add_to_log_changes)


def graph_obj_to_string(graph: dict, size_x: int = None, size_y: int = None, range_x: Range = None,
                        range_y: Range = None):
    return graph_to_string(graph['name'],
                           [GraphPoint(point['x'], point['y']) for point in graph['content']],
                           size_x, size_y, range_x, range_y)


class ProgramApiHandler(ApiHTTPRequestHandler):
    def get_api_dict(self) -> dict:
        return {
            'api': {
                'index.esp': 'command://get_api_dict',
                'config': {
                    'getConfigMap.esp': 'command://get_config_map',
                    'getConfig.esp': 'command://get_config',
                    'updateConfig.esp': 'command://update_config'
                },
                'actions': {
                    'getActions.esp': 'command://get_actions',
                    'executeAction.esp': 'command://exec_action'
                },
                'pause': {
                    'isPaused.esp': 'command://is_paused',
                    'pause.esp': 'command://pause',
                    'resume.esp': 'command://resume'
                },
                'utils': {
                    'getLogChanges.esp': 'command://get_log_changes',
                    'getNewGraphs.esp': 'command://get_new_graphs',
                    'getHWInfo.esp': 'command://get_hw_info'
                }
            }
        }

    def get_api_actions(self) -> dict:
        return {}

    def get_config_map(self) -> dict:
        return {}

    def get_config(self) -> dict:
        return {}

    def update_config(self, config: dict):
        pass

    def is_paused(self) -> bool:
        return True

    def pause(self):
        pass

    def resume(self):
        pass

    def get_new_graphs(self) -> list:
        return []

    def get_hw_info(self) -> dict:
        return {}

    def command_get_config(self, path, post_args, get_args):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        if self.command != 'HEAD':
            self.wfile.write(json.dumps(self.get_config()).encode())

        return True

    def command_update_config(self, path, post_args, get_args):
        if 'config' not in post_args:
            return False
        config = json.loads(post_args['config'])

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        if self.command != 'HEAD':
            try:
                self.update_config(config)
                self.wfile.write(json.dumps({'success': True}).encode())
            except Exception as e:
                log.exception(e)
                self.wfile.write(json.dumps({'success': False}).encode())

        return True

    def command_get_actions(self, path, post_args, get_args):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        if self.command != 'HEAD':
            self.wfile.write(json.dumps(list(self.get_api_actions().keys())).encode())

        return True

    def command_exec_action(self, path, post_args, get_args):
        if 'name' not in post_args:
            return False
        name = post_args['name']
        actions = self.get_api_actions()
        if name not in actions:
            return False

        method_name = 'action_' + actions[name]
        if not hasattr(self, method_name):
            return False
        method = getattr(self, method_name)
        return method(path, post_args, get_args)

    def command_is_paused(self, path, post_args, get_args):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        if self.command != 'HEAD':
            try:
                paused = self.is_paused()
                self.wfile.write(json.dumps({'success': True, 'paused': paused}).encode())
            except Exception as e:
                log.exception(e)
                self.wfile.write(json.dumps({'success': False}).encode())

        return True

    def command_pause(self, path, post_args, get_args):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        if self.command != 'HEAD':
            try:
                self.pause()
                self.wfile.write(json.dumps({'success': True}).encode())
            except Exception as e:
                log.exception(e)
                self.wfile.write(json.dumps({'success': False}).encode())

        return True

    def command_resume(self, path, post_args, get_args):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        if self.command != 'HEAD':
            try:
                self.resume()
                self.wfile.write(json.dumps({'success': True}).encode())
            except Exception as e:
                log.exception(e)
                self.wfile.write(json.dumps({'success': False}).encode())

        return True

    def command_get_log_changes(self, path, post_args, get_args):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        if self.command != 'HEAD':
            try:
                global LOG_CHANGES
                log_changes = LOG_CHANGES
                LOG_CHANGES = ''
                self.wfile.write(json.dumps({'success': True, 'result': log_changes}).encode())
            except Exception as e:
                log.exception(e)
                self.wfile.write(json.dumps({'success': False}).encode())

        return True

    def command_get_new_graphs(self, path, post_args, get_args):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        if self.command != 'HEAD':
            try:
                self.wfile.write(json.dumps({'success': True, 'result': self.get_new_graphs()}).encode())
            except Exception as e:
                log.exception(e)
                self.wfile.write(json.dumps({'success': False}).encode())

        return True

    def command_get_hw_info(self, path, post_args, get_args):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        if self.command != 'HEAD':
            try:
                self.wfile.write(json.dumps({'success': True, 'result': self.get_hw_info()}).encode())
            except Exception as e:
                log.exception(e)
                self.wfile.write(json.dumps({'success': False}).encode())

        return True


class Program:
    SERVER_PORT = 8000

    def __init__(self, request_handler_class=ApiHTTPRequestHandler):
        if DEBUG_MODE:
            self._server = HTTPServer(('', self.SERVER_PORT), request_handler_class)
            self._server.timeout = 5
        else:
            self._server = None
        self._request_stop_event = Event()
        self._stopped_event = Event()
        self._stopped_event.set()

    def _on_start(self, config: dict = None):
        pass

    def _on_exit(self):
        pass

    def is_running(self):
        return not self._stopped_event.is_set()

    def can_start(self):
        return not self.is_running()

    def wait_to_exit(self):
        self._stopped_event.wait()

    def start(self, config: dict = None):
        if not self.can_start():
            return False

        self._request_stop_event.clear()
        self._stopped_event.clear()

        def run_server():
            try:
                self._on_start(config)
                self._server.serve_forever() if DEBUG_MODE else self._request_stop_event.wait()
            except (KeyboardInterrupt, Exception) as e:
                log.exception(e)
            finally:
                self._on_exit()
                self._running = False
                self._stopped_event.set()
                self._request_stop_event.clear()

        Thread(target=run_server).start()
        log.info("Started HTTP server on port %d" % self.SERVER_PORT if DEBUG_MODE else "Program started...")
        return True

    def exit(self):
        if self.is_running():
            self._server.shutdown() if self._server is not None else None
            self._request_stop_event.set()

    def __del__(self):
        try:
            self._server.server_close() if self._server is not None else None
        except Exception as e:
            pass
