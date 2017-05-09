#!/usr/bin/env python3
from utils.log import get_logger

log = get_logger(__name__)

if __name__ == '__main__':
    from sumo_robot.hardware.gui import show as show_gui

    show_gui()
    from sumo_robot.program import run

    run()
