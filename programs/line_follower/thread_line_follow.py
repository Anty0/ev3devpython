import math
import time

from hardware.hw_config import SCANNER_REFLECT_HEAD_POSITION, SCANNER_DISTANCE_PROPULSION_POSITION
from utils.calc.position import Position2D
from utils.control.odometry import OdometryCalculator
from utils.control.pilot import Pilot
from utils.log import get_logger
from utils.sensor.scanner import Scanner
from utils.threading.co_working_threads import ShareAccessInterface

log = get_logger(__name__)


def perform_simple_scan(pilot: Pilot, scanner_reflect: Scanner) -> dict:
    results = []

    def scan_reflect():
        read = scanner_reflect.value(percent=False)
        positions = pilot.get_positions()
        results.append({'reflect': read, 'wheels_positions': positions})
        time.sleep(0)

    start_position = pilot.get_positions()

    pilot.run_percent_drive_to_angle_deg(45, 200, speed_mul=0.05)
    pilot.wait_to_stop()
    time.sleep(0.25)

    pilot.run_percent_drive_to_angle_deg(90, -200, speed_mul=0.025)
    pilot.repeat_while_running(scan_reflect)
    time.sleep(0.25)

    pilot.run_percent_drive_to_angle_deg(45, 200, speed_mul=0.05)
    pilot.wait_to_stop()
    time.sleep(0.25)

    return {'start_position': start_position, 'results': results}


def perform_detailed_line_scan(shared: ShareAccessInterface, pilot: Pilot, scanner_reflect: Scanner):
    if scanner_reflect.motor_connected:
        scanner_reflect.rotate_to_abs_pos(0)
        scanner_reflect.wait_to_stop()

    scan_result = perform_simple_scan(pilot, scanner_reflect)

    if len(scan_result) == 0:
        return None

    min_reflect = 100
    max_reflect = 0
    for result in scan_result['results']:
        reflect = result['reflect']
        min_reflect = min(min_reflect, reflect)
        max_reflect = max(max_reflect, reflect)
    scan_result['min_reflect'] = min_reflect
    scan_result['max_reflect'] = max_reflect

    sensor_pos_distance = SCANNER_REFLECT_HEAD_POSITION.distance_to(Position2D(0, 0, 0))
    start_position = scan_result['start_position']
    start_position_len = len(start_position)

    min_reflect_result = None
    for result in scan_result['results']:
        if result['reflect'] == min_reflect:
            min_reflect_result = result
    min_reflect_wheels_positions = min_reflect_result['wheels_positions']
    min_reflect_positions_change = [min_reflect_wheels_positions[i] - start_position[i]
                                    for i in range(start_position_len)]
    min_reflect_angle = pilot.positions_change_to_angle(min_reflect_positions_change)
    min_reflect_pos = math.sin(math.radians(min_reflect_angle)) * sensor_pos_distance
    position_offset = min_reflect_pos
    scan_result['position_offset'] = position_offset

    for result in scan_result['results']:
        wheels_positions = result['wheels_positions']
        positions_change = [wheels_positions[i] - start_position[i] for i in range(start_position_len)]

        angle = pilot.positions_change_to_angle(positions_change)

        position = (math.sin(math.radians(angle)) * sensor_pos_distance) - position_offset
        # position_int = round(position * 1000)

        result['wheels_positions_change'] = positions_change
        result['angle'] = angle
        result['position'] = position
        # result['position_int'] = position_int

    diff_reflect = max_reflect - min_reflect
    filter_min_reflect = round(min_reflect + (diff_reflect / 5))
    filter_max_reflect = round(max_reflect - (diff_reflect / 5))
    scan_result['filtered_results'] = \
        list(filter(lambda o: filter_min_reflect <= o['reflect'] <= filter_max_reflect, scan_result['results']))

    min_position = max_position = 0
    # min_position_int = max_position_int = 0
    for result in scan_result['filtered_results']:
        position = result['position']
        min_position = min(min_position, position)
        max_position = max(max_position, position)

        # position_int = result['position_int']
        # min_position_int = min(min_position_int, position_int)
        # max_position_int = max(max_position_int, position_int)

    scan_result['min_position'] = min_position
    scan_result['max_position'] = max_position

    # scan_result['min_position_int'] = min_position_int
    # scan_result['max_position_int'] = max_position_int

    # scan_result['sorted_results'] = sorted(scan['results'], key=lambda o: o['position'])

    # position_to_reflect_list = [[] for i in range(min_position_int, max_position_int + 1)]
    # for result in scan_result['filtered_results']:
    #     position_to_reflect_list[result['position_int']].append(result['reflect'])
    #
    # for i in range(min_position_int, max_position_int + 1):
    #     results_on_position = position_to_reflect_list[i]
    #     if len(results_on_position) == 0:
    #         position_to_reflect_list[i] = None
    #         continue
    #     position_to_reflect_list[i] = functools.reduce(
    #         lambda x, y: x + y, results_on_position) / len(results_on_position)
    #
    # def distance_to_not_none(i, change):
    #     pos = i + change
    #     while min_position_int <= pos <= max_position_int \
    #             and position_to_reflect_list[pos] is None:
    #         pos += change
    #     if pos < min_position_int or pos > max_position_int:
    #         return None
    #     return pos - i
    #
    # for i in range(min_position_int, max_position_int + 1):
    #     if position_to_reflect_list[i] is not None:
    #         continue
    #     distance_left = distance_to_not_none(i, -1)
    #     distance_right = distance_to_not_none(i, 1)
    #     if distance_left is None or distance_right is None:
    #         continue
    #     reflect_left = position_to_reflect_list[i + distance_left]
    #     reflect_right = position_to_reflect_list[i + distance_right]
    #     change_reflect = reflect_right - reflect_left
    #     change_distance = distance_right - distance_left
    #     position_to_reflect_list[i] = (change_reflect / change_distance * -distance_left) + reflect_left
    #
    # scan_result['position_to_reflect_list'] = position_to_reflect_list

    reflect_to_position_list = [[] for i in range(101)]
    for result in scan_result['filtered_results']:
        reflect_to_position_list[result['reflect']].append(result['position'])

    for i in range(len(reflect_to_position_list)):
        position_with_reflect = min(filter(lambda o: o >= 0, reflect_to_position_list[i]), default=None)
        reflect_to_position_list[i] = position_with_reflect

    def distance_to_not_none(i, change):
        pos = i + change
        while 0 <= pos <= 100 and reflect_to_position_list[pos] is None:
            pos += change
        if pos < 0 or pos > 100:
            return None
        return pos - i

    for i in range(len(reflect_to_position_list)):
        if reflect_to_position_list[i] is not None:
            continue
        distance_left = distance_to_not_none(i, -1)
        distance_right = distance_to_not_none(i, 1)
        if distance_left is None:
            reflect_to_position_list[i] = 0
            continue
        if distance_right is None:
            reflect_to_position_list[i] = max_position
            continue
        position_left = reflect_to_position_list[i + distance_left]
        position_right = reflect_to_position_list[i + distance_right]
        change_position = position_right - position_left
        change_distance = distance_right - distance_left
        reflect_to_position_list[i] = (change_position / change_distance * -distance_left) + position_left

    scan_result['reflect_to_position_list'] = reflect_to_position_list

    shared.data.add_new_graph({
        'name': 'Reflect by angle scan',
        'content': [{'x': result['angle'], 'y': result['reflect']} for result in scan_result['results']]
    })
    shared.data.add_new_graph({
        'name': 'Reflect by position scan',
        'content': [{'x': result['position'], 'y': result['reflect']} for result in scan_result['results']]
    })
    shared.data.add_new_graph({
        'name': 'Reflect by position filtered scan',
        'content': [{'x': result['position'], 'y': result['reflect']} for result in scan_result['filtered_results']]
    })
    # shared.data.add_new_graph({
    #     'name': 'Position to reflect scan',
    #     'content': [{'x': j, 'y': scan_result['position_to_reflect_list'][j]}
    #                 for j in range(scan_result['min_position_int'], scan_result['max_position_int'])]
    # })
    shared.data.add_new_graph({
        'name': 'Reflect to position scan',
        'content': [{'x': j, 'y': scan_result['reflect_to_position_list'][j]}
                    for j in range(len(scan_result['reflect_to_position_list']))]
    })
    return {
        'max_position': scan_result['max_position'],
        # 'max_position_int': scan_result['max_position_int'],
        'position_offset': scan_result['position_offset'],
        'min_reflect': scan_result['min_reflect'],
        'max_reflect': scan_result['max_reflect'],
        # 'position_to_reflect_list': scan_result['position_to_reflect_list'],
        'reflect_to_position_list': scan_result['reflect_to_position_list'],
    }


def run_loop(shared: ShareAccessInterface):
    pilot = shared.data.pilot
    scanner_reflect = shared.data.scanner_reflect

    runtime_config = shared.data.config
    config = runtime_config.extract_config_values(
        'TARGET_POWER', 'TARGET_POSITION', 'LINE_SIDE', 'TARGET_CYCLE_TIME'
    )
    # config = runtime_config.extract_config_values(
    #     'REG_STEER_P', 'REG_STEER_I', 'REG_STEER_D',
    #     'TARGET_POWER', 'TARGET_REFLECT', 'LINE_SIDE', 'TARGET_CYCLE_TIME'
    # )
    # detect_reflect = runtime_config.get_config_value('DETECT_REFLECT')
    # min_reflect = runtime_config.get_config_value('MIN_REFLECT')
    # max_reflect = runtime_config.get_config_value('MAX_REFLECT')
    # min_to_max_distance = runtime_config.get_config_value('MIN_TO_MAX_DISTANCE')

    # if detect_reflect:
    line_info = shared.data.line_info
    target_position = 0

    def update_target_position():
        global target_position, line_info
        target_position = config['TARGET_POSITION'] / 100 * line_info['max_position']

    def perform_line_scan():
        global line_info
        shared.data.perform_line_scan = False
        line_info = perform_detailed_line_scan(shared, pilot, scanner_reflect)
        shared.data.line_info = line_info
        update_target_position()

        sensor_pos_distance = SCANNER_REFLECT_HEAD_POSITION.distance_to(Position2D(0, 0, 0))
        angle_fix = math.degrees(math.asin((line_info['position_offset'] - target_position) / sensor_pos_distance))
        if angle_fix != 0:
            pilot.run_percent_drive_to_angle_deg(abs(angle_fix), 200 + (angle_fix / abs(angle_fix)), speed_mul=0.05)

    perform_line_scan()

    # regulator_steer = RangeRegulator(getter_p=lambda: config['REG_STEER_P'],
    #                                  getter_i=lambda: config['REG_STEER_I'],
    #                                  getter_d=lambda: config['REG_STEER_D'],
    #                                  getter_target=lambda: config['TARGET_REFLECT'])
    #
    # regulator_sensor = None  # TODO: create, rework and and test

    odometry = OdometryCalculator(*pilot.wheels)

    sensor_head_pos_distance = SCANNER_REFLECT_HEAD_POSITION.distance_to(SCANNER_DISTANCE_PROPULSION_POSITION)
    try:
        pilot.run_direct()
        # last_time = time.time()
        while shared.should_run():
            if runtime_config.update_extracted_config(config):
                update_target_position()
                # regulator_steer.reset()

            odometry.cycle()

            read_val = scanner_reflect.value(percent=False)
            line_distance = line_info['reflect_to_position_list'][read_val]
            target_pos_distance = line_distance - line_info['max_position'] / 100 * config['TARGET_POSITION']
            angle_to_line = math.degrees(math.asin(target_pos_distance / sensor_head_pos_distance))
            scanner_reflect.rotate_to_rel_pos(angle_to_line)
            # TODO: complete implementation

            # read_val = scanner_reflect.value(percent=False)
            # read_percent = 100 * (read_val - min_reflect) / (max_reflect - min_reflect)
            # course = crop_r(regulator_steer.regulate(read_percent) * config['LINE_SIDE'])
            #
            # if shared.data.pause:
            #     pilot.update_duty_cycle(course, target_duty_cycle=0, mul_duty_cycle=config['TARGET_POWER'] / 100)
            # else:
            #     pilot.update_duty_cycle(course, mul_duty_cycle=config['TARGET_POWER'] / 100)

            if shared.data.perform_line_scan:
                pilot.stop()

                time.sleep(5)
                perform_line_scan()

                # regulator_steer.reset()
                pilot.run_direct()
                # last_time = time.time()

            if shared.should_pause():
                pilot.stop()

                shared.wait_resume()

                # regulator_steer.reset()
                pilot.run_direct()
                # last_time = time.time()
                #
                # last_time = wait_to_cycle_time('line_follow', last_time, config['TARGET_CYCLE_TIME'])
    finally:
        pilot.stop()
