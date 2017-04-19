import time
from threading import Event

from .log import get_logger

log = get_logger(__name__)

DEBUG_CYCLE_TIME = False


def wait_to_cycle_time(cycle_name: str, last_time: float, cycle_time: float):
    new_time = time.time()
    sleep_time = cycle_time - (new_time - last_time)
    if sleep_time > 0:
        time.sleep(sleep_time)
        last_time += cycle_time
    elif DEBUG_CYCLE_TIME:
        if sleep_time < -cycle_time * 5:
            log.warning('Cycle {} is getting late. It\'s late {:f} seconds. Use bigger cycle time.'
                        .format(cycle_name, -sleep_time))
        last_time += cycle_time
    else:
        last_time = new_time
    return last_time


def crop_m(input_val, min_out=-100, max_out=100):
    return min(max_out, max(min_out, input_val))


def crop_r(input_val, max_r=100):
    return min(max_r, max(-max_r, input_val))


def repeat_while(condition: callable, callback: callable, stop_event: Event = None):
    if stop_event is not None:
        stop_event.clear()
    try:
        while condition():
            callback()
    finally:
        if stop_event is not None:
            stop_event.set()
