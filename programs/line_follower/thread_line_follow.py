import math
import time

from ev3dev.auto import Button

from hardware.brick_scanner_reflect import BRICK_SCANNER_REFLECT_SENSOR, BRICK_SCANNER_REFLECT_PROPULSION
from utils.control.odometry import PositionsCollector, from_wheels as odometry_from_wheels
from utils.control.pilot import Pilot
from utils.debug_mode import DEBUG_MODE
from utils.graph import graph_to_string, GraphPoint
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

    if len(scan_result['results']) == 0:
        return None

    min_reflect = 100
    max_reflect = 0
    for result in scan_result['results']:
        reflect = result['reflect']
        min_reflect = min(min_reflect, reflect)
        max_reflect = max(max_reflect, reflect)
    scan_result['min_reflect'] = min_reflect
    scan_result['max_reflect'] = max_reflect

    pos_center_to_sensor_distance = BRICK_SCANNER_REFLECT_SENSOR.position.get(None).point.distance()
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
    min_reflect_pos = math.sin(math.radians(min_reflect_angle)) * pos_center_to_sensor_distance
    position_offset = min_reflect_pos
    scan_result['position_offset'] = position_offset

    for result in scan_result['results']:
        wheels_positions = result['wheels_positions']
        positions_change = [wheels_positions[i] - start_position[i] for i in range(start_position_len)]

        angle = pilot.positions_change_to_angle(positions_change)

        position = (math.sin(math.radians(angle)) * pos_center_to_sensor_distance) - position_offset
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

    if DEBUG_MODE:
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

    line_info = shared.data.line_info
    target_position = 0

    def update_target_position():
        global target_position, line_info
        target_position = config['TARGET_POSITION'] / 100 * line_info['max_position']

    def perform_line_scan():
        log.info('Starting line scan...')
        global line_info
        shared.data.perform_line_scan = False
        scan_result = perform_detailed_line_scan(shared, pilot, scanner_reflect)
        if scan_result is None:
            return False

        line_info = scan_result
        shared.data.line_info = line_info
        update_target_position()

        log.info('Fixing robot position...')
        pos_center_to_sensor_distance = BRICK_SCANNER_REFLECT_SENSOR.position.get(None).distance()
        angle_fix = math.degrees(math.asin(
            (line_info['position_offset'] - target_position) / pos_center_to_sensor_distance
        ))
        if angle_fix != 0:
            pilot.run_percent_drive_to_angle_deg(abs(angle_fix), 200 + (angle_fix / abs(angle_fix)), speed_mul=0.05)
        return True

    if not perform_line_scan():
        log.info('Line scan failed, exiting loop...')  # TODO: create default line info
        return

    odometry = odometry_from_wheels(*pilot.wheels)
    robot_positions_collector = PositionsCollector(odometry) if DEBUG_MODE else None
    line_positions = []

    sensor_position = BRICK_SCANNER_REFLECT_SENSOR.position.get(None)
    propulsion_position = BRICK_SCANNER_REFLECT_PROPULSION.position.get(None)

    pos_center_to_propulsion_angle_rad = propulsion_position.angle.rad_z
    pos_center_to_propulsion_distance = propulsion_position.point.distance()

    pos_propulsion_to_sensor_angle_rad = sensor_position.angle.rad_z - pos_center_to_propulsion_angle_rad
    pos_propulsion_to_sensor_distance = propulsion_position.point.distance(sensor_position)

    pos_sensor_to_line_angle_rad = math.radians(-90)
    try:
        if not DEBUG_MODE:
            log.info('Line follower is ready')
            log.info('Waiting on enter press...')
            while not Button.enter:
                time.sleep(0)
            time.sleep(0.2)

        pilot.run_direct()
        while shared.should_run():
            if runtime_config.update_extracted_config(config):
                update_target_position()

            odometry.cycle()
            if DEBUG_MODE:
                robot_positions_collector.cycle()
            val_reflect = scanner_reflect.value(percent=False)
            pos_scanner_angle_deg = scanner_reflect.angle_deg()
            pos_scanner_angle_rad = math.radians(pos_scanner_angle_deg)

            pos_line_side = config['LINE_SIDE']
            pos_line_center_distance = line_info['reflect_to_position_list'][val_reflect]
            pos_line_target_distance = pos_line_center_distance - target_position

            if DEBUG_MODE:
                pos_robot = odometry.position

                pos_propulsion_angle_rad = pos_robot[2] + pos_center_to_propulsion_angle_rad
                pos_propulsion_x = pos_robot[0] + math.cos(pos_propulsion_angle_rad) * pos_center_to_propulsion_distance
                pos_propulsion_y = pos_robot[1] + math.sin(pos_propulsion_angle_rad) * pos_center_to_propulsion_distance

                pos_sensor_angle_rad = \
                    pos_propulsion_angle_rad + pos_propulsion_to_sensor_angle_rad + pos_scanner_angle_rad
                pos_sensor_x = pos_propulsion_x + math.cos(pos_sensor_angle_rad) * pos_propulsion_to_sensor_distance
                pos_sensor_y = pos_propulsion_y + math.sin(pos_sensor_angle_rad) * pos_propulsion_to_sensor_distance

                pos_line_target_angle = pos_sensor_angle_rad + pos_sensor_to_line_angle_rad * pos_line_side
                pos_line_target_x = pos_sensor_x + math.cos(pos_line_target_angle) * pos_line_target_distance
                pos_line_target_y = pos_sensor_y + math.sin(pos_line_target_angle) * pos_line_target_distance

                line_positions.append([pos_line_target_x, pos_line_target_y])

            angle_to_line = math.degrees(
                math.asin(pos_line_target_distance / pos_propulsion_to_sensor_distance) * pos_line_side
            )
            scanner_reflect.rotate_to_rel_pos(angle_to_line)

            ch_x = math.sin(pos_scanner_angle_rad) * pos_propulsion_to_sensor_distance
            ch_y = pos_center_to_propulsion_distance + (
                math.cos(pos_scanner_angle_rad) * pos_propulsion_to_sensor_distance
            )
            course_r = (ch_x ** 2 + ch_y ** 2) / (2 * ch_x) if ch_x != 0 else None
            # None course_r causes strait a head drive

            if shared.data.pause:
                pilot.update_duty_cycle_unit(course_r, target_duty_cycle=0, max_duty_cycle=config['TARGET_POWER'])
                # pilot.update_duty_cycle(course, target_duty_cycle=0, mul_duty_cycle=config['TARGET_POWER'] / 100)
            else:
                pilot.update_duty_cycle_unit(course_r, max_duty_cycle=config['TARGET_POWER'])
                # pilot.update_duty_cycle(course, mul_duty_cycle=config['TARGET_POWER'] / 100)

            if shared.data.perform_line_scan:
                pilot.stop()
                time.sleep(5)
                if not perform_line_scan():
                    log.info('Line scan failed, old result will be used.')
                pilot.run_direct()

            if shared.should_pause():
                pilot.stop()
                shared.wait_resume()
                pilot.run_direct()
    finally:
        pilot.stop()
        if DEBUG_MODE:
            print(graph_to_string('Robot positions', [
                GraphPoint(point[0], point[1]) for point in robot_positions_collector.positions
            ]))
            print(graph_to_string('Line positions', [
                GraphPoint(point[0], point[1]) for point in line_positions
            ]))
