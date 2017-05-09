#!/usr/bin/env python3
import sys

from main_robot.programs import PROGRAMS
from utils.log import get_logger
from utils.program import start_program_from_args

log = get_logger(__name__)

if __name__ == '__main__':
    from main_robot.hardware.gui import show as show_gui

    show_gui()
    start_program_from_args(sys.argv, PROGRAMS)
