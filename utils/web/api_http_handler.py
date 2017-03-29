import cgi
import json
import mimetypes
import os
import shutil
import urllib.parse
from http.server import BaseHTTPRequestHandler

from utils.log import get_logger

log = get_logger(__name__)


class ApiHTTPRequestHandler(BaseHTTPRequestHandler):
    def log_error(self, format, *args):
        log.error(format % args)
        pass

    # def log_message(self, format, *args):
    #     log.debug(format % args)
    #     pass

    def get_api_dict(self) -> dict:
        return {'index.esp': 'command://get_api_dict'}

    def resolve_path(self, path) -> str or dict or None:
        path = path.split(os.sep)
        if path[0] == '':
            path.pop(0)

        file_contents = self.get_api_dict()
        for filename in path:
            if not self.is_dir(file_contents):
                return None
            if filename not in file_contents:
                if not len(filename):
                    for other_filename in ['index.esp', 'index.html']:
                        if other_filename in file_contents and not self.is_dir(file_contents[other_filename]):
                            filename = other_filename
                            break

                    if not len(filename):
                        return None
                else:
                    return None
            file_contents = file_contents[filename]
        return file_contents

    def is_dir(self, file):
        return isinstance(file, dict)

    def is_api_call(self, file):
        return isinstance(file, str) and file.startswith('command://')

    def is_file(self, file):
        return isinstance(file, str) and file.startswith('file://')

    def is_path_dir(self, path):
        return self.is_dir(self.resolve_path(path))

    def is_path_api_call(self, path):
        return self.is_api_call(self.resolve_path(path))

    def is_path_file(self, path):
        return self.is_file(self.resolve_path(path))

    def get_command_name_from_path(self, path):
        return path[10::]

    def get_file_path_from_path(self, path):
        return path[7::]

    def resolve_post_args(self):
        content_type_header = self.headers.get('content-type')
        if content_type_header is None:
            return {}

        content_type, options_dictionary = cgi.parse_header(content_type_header)
        if content_type == 'multipart/form-data':
            post_args = cgi.parse_multipart(self.rfile, options_dictionary)
        elif content_type == 'application/x-www-form-urlencoded':
            length = int(self.headers.get('content-length'))
            post_args = urllib.parse.parse_qs(self.rfile.read(length), keep_blank_values=True)
        else:
            post_args = {}

        return post_args

    def resolve_url_info(self):
        url_info = urllib.parse.urlparse(self.path)
        result = type('UrlInfo', (object,), {})()
        result.scheme, result.netloc, result.path, result.params, result.query, result.fragment \
            = url_info.scheme, url_info.netloc, url_info.path, url_info.params, url_info.query, url_info.fragment
        result.args = urllib.parse.parse_qs(url_info.query)
        return result

    def try_handle_request(self, path, post_args, get_args):
        path_result = self.resolve_path(path)
        if path_result is not None:
            # noinspection PyTypeChecker
            if self.is_dir(path_result):
                return False
            elif self.is_api_call(path_result):
                method_name = 'command_' + self.get_command_name_from_path(path_result)
                if not hasattr(self, method_name):
                    return False
                method = getattr(self, method_name)
                return method(path, post_args, get_args)
            elif self.is_file(path_result):
                file_path = self.get_file_path_from_path(path_result)
                mime_type, encoding = mimetypes.guess_type(file_path)
                if mime_type is None:
                    mime_type = 'text/plain'

                self.send_response(200)
                self.send_header('Content-type', mime_type)
                self.end_headers()

                if self.command != 'HEAD':
                    with open(file_path, mode='rb') as fh:
                        shutil.copyfileobj(fh, self.wfile)
                return True
            else:
                return False
        else:
            self.send_error(404, 'File Not Found: %s' % path)
            return True

    def handle_request(self, path, post_args, get_args):
        if not self.try_handle_request(path, post_args, get_args):
            self.send_error(404, 'Can\'t handle: %s' % path)

    def do_HEAD(self):
        url_info = self.resolve_url_info()
        self.handle_request(url_info.path, {}, url_info.args)

    def do_POST(self):
        url_info = self.resolve_url_info()
        self.handle_request(url_info.path, self.resolve_post_args(), url_info.args)

    def do_GET(self):
        url_info = self.resolve_url_info()
        self.handle_request(url_info.path, {}, url_info.args)

    def command_get_api_dict(self, path, post_args, get_args):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        if self.command != 'HEAD':
            self.wfile.write(json.dumps(self.get_api_dict()).encode())

        return True
