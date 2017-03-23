#!/usr/bin/env python3

import signal
import sys
from collections import OrderedDict

from programs.line_follower import LineFollowProgram
from utils.log import get_logger

log = get_logger(__name__)

PROGRAMS = OrderedDict()
PROGRAMS['line_follower'] = {
    'class': LineFollowProgram,
    'help_text': ''
}
PROGRAMS['auto_driver'] = {
    'class': None,
    'help_text': ''
}
PROGRAMS['remote_control'] = {
    'class': None,
    'help_text': ''
}


def run():
    program_name_pos = sys.argv.index('--run') + 1 if '--run' in sys.argv else -1
    program_name = sys.argv[program_name_pos] if program_name_pos != -1 and len(sys.argv) > program_name_pos else None
    program_info = PROGRAMS[program_name] if program_name in PROGRAMS else None

    if '--help' in sys.argv or '-h' in sys.argv:
        if program_info is None:
            print('Usages: Run program   - ./main.py --run program_name [--simulate|-s]\n' +
                  '        About program - ./main.py --run program_name --help|-h\n' +
                  '        This help     - ./main.py [--help|-h]\n\n' +
                  'Available programs:\n' +
                  '\n'.join(['    ' + name for name in PROGRAMS.keys()]))
        else:
            print('Help for program ' + program_name + ':\n' +
                  program_info['help_text'])
        exit()

    if program_info is None:
        print('Can\'t start requested program: Check program name.')
        exit(1)

    program_class = program_info['class']
    if program_class is None:
        print('Can\'t start requested program: Program is not implemented.')
        exit(1)

    program = program_class()
    program.start()

    def handle_exit(signum, frame):
        program.exit()
        program.wait_to_exit()

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)


if __name__ == '__main__':
    run()
