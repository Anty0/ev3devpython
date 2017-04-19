from collections import OrderedDict

from programs.line_follower.program import LineFollowProgram

PROGRAMS = OrderedDict()
PROGRAMS['line_follower'] = {
    'class': LineFollowProgram,
    'additional_args': ['--simulate', ['--hw-normal', '--hw-fast'], '--debug'],
    'help_text': 'Program that forces robot to follow black (or theoretically white) line.'
}
PROGRAMS['auto_driver'] = {
    'class': None,
    'additional_args': ['--simulate', ['--hw-normal', '--hw-fast'], '--debug'],
    'help_text': 'Program that tries to ride a robot without collisions.'
}
PROGRAMS['remote_control'] = {
    'class': None,
    'additional_args': ['--simulate', ['--hw-normal', '--hw-fast'], '--debug'],
    'help_text': 'Program that allows you to force robot to move as you want.'
}
