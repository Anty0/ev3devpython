from collections import OrderedDict

THREAD_LINE_FOLLOW_NAME = 'line_follow'
THREAD_COLLISION_AVOID_NAME = 'collision_avoid'

CONFIG_VALUES = OrderedDict()
CONFIG_VALUES['AUTO_LEARN_CONSTANTS'] = {
    'category': 'Steer regulation', 'display_name': 'Try auto-learn constants (beta)',
    'type': 'bool', 'default_value': False  # TODO: add support
}
CONFIG_VALUES['REG_STEER_P'] = {
    'category': 'Steer regulation', 'display_name': 'Regulator STEER-P',
    'type': 'float', 'default_value': float(0.3)  # Proportional gain. Start value 1
}
CONFIG_VALUES['REG_STEER_I'] = {
    'category': 'Steer regulation', 'display_name': 'Regulator STEER-I',
    'type': 'float', 'default_value': float(0)  # Integral gain. Start value 0
}
CONFIG_VALUES['REG_STEER_D'] = {
    'category': 'Steer regulation', 'display_name': 'Regulator STEER-D',
    'type': 'float', 'default_value': float(0)  # Derivative gain. Start value 0
}
CONFIG_VALUES['PAUSE_POWER'] = {
    'category': 'Power', 'display_name': 'Pause',
    'type': 'bool', 'default_value': True
}
CONFIG_VALUES['TARGET_POWER'] = {
    'category': 'Power', 'display_name': 'Target power',
    'type': 'int', 'default_value': 20
}
CONFIG_VALUES['TARGET_REFLECT'] = {
    'category': 'Color sensor', 'display_name': 'Target reflection',
    'type': 'int', 'default_value': 55
}
CONFIG_VALUES['DETECT_REFLECT'] = {
    'category': 'Color sensor', 'display_name': 'Auto detect min/max reflection',
    'type': 'bool', 'default_value': True
}
CONFIG_VALUES['MIN_REFLECT'] = {
    'category': 'Color sensor', 'display_name': 'Minimal reflection',
    'type': 'int', 'default_value': 0
}
CONFIG_VALUES['MAX_REFLECT'] = {
    'category': 'Color sensor', 'display_name': 'Maximal reflection',
    'type': 'int', 'default_value': 100
}
CONFIG_VALUES['MIN_TO_MAX_DISTANCE'] = {
    'category': 'Color sensor', 'display_name': 'Distance from min to max',
    'type': 'int', 'default_value': 1  # TODO: better default value
}
CONFIG_VALUES['OBSTACLE_AVOID'] = {
    'category': 'Obstacle', 'display_name': 'Obstacle avoid',
    'type': 'bool', 'default_value': False
}
CONFIG_VALUES['OBSTACLE_AVOID_SIDE'] = {
    'category': 'Obstacle', 'display_name': 'Obstacle avoid side',
    'type': 'enum', 'enum_options': {
        'left': -1,
        'right': 1
    }, 'default_value': -1  # -1 == left; 1 == right
}
CONFIG_VALUES['OBSTACLE_MIN_DISTANCE'] = {
    'category': 'Obstacle', 'display_name': 'Minimal distance from obstacle',
    'type': 'int', 'default_value': 25
}
CONFIG_VALUES['OBSTACLE_WIDTH'] = {
    'category': 'Obstacle', 'display_name': 'Width of obstacle',
    'type': 'float', 'default_value': 0  # 0 = automatic detection
}
CONFIG_VALUES['OBSTACLE_HEIGHT'] = {
    'category': 'Obstacle', 'display_name': 'Height of obstacle',
    'type': 'float', 'default_value': 0  # 0 = automatic detection
}
CONFIG_VALUES['COLLISION_AVOID'] = {
    'category': 'Collision', 'display_name': 'Robot collision avoid',
    'type': 'bool', 'default_value': False
}
CONFIG_VALUES['LINE_SIDE'] = {
    'category': 'Other', 'display_name': 'Line side',
    'type': 'enum', 'enum_options': {
        'left': -1,
        'right': 1
    }, 'default_value': -1  # -1 == left; 1 == right
}
CONFIG_VALUES['TARGET_CYCLE_TIME'] = {
    'category': 'Other', 'display_name': 'Target cycle time',
    'type': 'float', 'default_value': 0.05
}
