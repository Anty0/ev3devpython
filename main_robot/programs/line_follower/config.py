from collections import OrderedDict

THREAD_LINE_FOLLOW_NAME = 'line_follow'
THREAD_COLLISION_AVOID_NAME = 'collision_avoid'
CONFIG_VALUES = OrderedDict()

CONFIG_VALUES['TARGET_POWER'] = {
    'category': 'Power', 'display_name': 'Target power',
    'type': 'int', 'default_value': 75
}

CONFIG_VALUES['TARGET_POSITION'] = {
    'category': 'Line follow', 'display_name': 'Target sensor position',
    'type': 'int', 'default_value': 55
}
CONFIG_VALUES['LINE_SIDE'] = {
    'category': 'Line follow', 'display_name': 'Line side',
    'type': 'enum', 'enum_options': {
        'left': -1,
        'right': 1
    }, 'default_value': 1  # -1 == left; 1 == right
}
CONFIG_VALUES['OBSTACLE_AVOID'] = {
    'category': 'Obstacle', 'display_name': 'Obstacle avoid',
    'type': 'bool', 'default_value': True
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
    'type': 'int', 'default_value': 50
}
CONFIG_VALUES['OBSTACLE_WIDTH'] = {
    'category': 'Obstacle', 'display_name': 'Width of obstacle',
    'type': 'float', 'default_value': 15  # 0 = automatic detection
}
CONFIG_VALUES['OBSTACLE_HEIGHT'] = {
    'category': 'Obstacle', 'display_name': 'Height of obstacle',
    'type': 'float', 'default_value': 18  # 0 = automatic detection
}

CONFIG_VALUES['COLLISION_AVOID'] = {
    'category': 'Collision', 'display_name': 'Robot collision avoid',
    'type': 'bool', 'default_value': False
}

CONFIG_VALUES['TARGET_CYCLE_TIME'] = {
    'category': 'Other', 'display_name': 'Target cycle time',
    'type': 'float', 'default_value': 0.05
}
