import logging

import sys

logging_listeners = []


class LoggingListener:
    def handle_msg(self, msg):
        pass


def add_logging_listener(listener):
    logging_listeners.append(listener)


class LogSteamHandler:
    def flush(self):
        sys.stdout.flush()
        pass

    def write(self, msg):
        sys.stdout.write(msg)
        for listener in logging_listeners:
            listener.handle_msg(msg)


root = logging.getLogger()
root.setLevel(logging.DEBUG)

# Enable logging output
ch = logging.StreamHandler(LogSteamHandler())
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


def get_logger(name=None):
    return logging.getLogger(name)
