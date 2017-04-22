import math
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


def list_line_points(start, end):
    """Bresenham's Line Algorithm
    Produces a list of tuples from start and end
 
    >>> points1 = list_line_points((0, 0), (3, 4))
    >>> points2 = list_line_points((3, 4), (0, 0))
    >>> assert(set(points1) == set(points2))
    >>> print(points1)
    [(0, 0), (1, 1), (1, 2), (2, 3), (3, 4)]
    >>> print(points2)
    [(3, 4), (2, 3), (1, 2), (1, 1), (0, 0)]
    """
    # Setup initial conditions
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1

    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)

    # Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1

    # Calculate error
    error = int(dx / 2.0)
    y_step = 1 if y1 < y2 else -1

    # Iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += y_step
            error += dx

    # Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()
    return points


def list_circle_points(x0, y0, radius, start_angle: float = 0, stop_angle: float = 360):
    x = radius
    y = 0
    err = 0
    points = []

    def append(point):
        angle = math.degrees(math.atan2(point[1], point[0]))
        if start_angle <= angle <= stop_angle:
            points.append(point)

    while x >= y:
        append((x0 + x, y0 + y))
        append((x0 + y, y0 + x))
        append((x0 - y, y0 + x))
        append((x0 - x, y0 + y))
        append((x0 - x, y0 - y))
        append((x0 - y, y0 - x))
        append((x0 + y, y0 - x))
        append((x0 + x, y0 - y))

        if err <= 0:
            y += 1
            err += 2 * y + 1
        else:
            x -= 1
            err -= 2 * x + 1

    return points


def repeat_while(condition: callable, callback: callable, stop_event: Event = None):
    if stop_event is not None:
        stop_event.clear()
    try:
        while condition():
            callback()
    finally:
        if stop_event is not None:
            stop_event.set()
