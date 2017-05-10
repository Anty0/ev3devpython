import time

from main_robot.hardware.brick_scanner_distance import BRICK_SCANNER_DISTANCE_SENSOR
from main_robot.programs.line_follower.config import THREAD_LINE_FOLLOW_NAME
from utils.calc.regulator import RangeRegulator
from utils.calc.size import Size
from utils.control.pilot import Pilot
from utils.log import get_logger
from utils.sensor.scanner import Scanner
from utils.threading.co_working_threads import ShareAccessInterface
from utils.utils import wait_to_cycle_time, crop_m

log = get_logger(__name__)


def detect_collision(config: dict, scanner_distance: Scanner):
    min_distance = config['OBSTACLE_MIN_DISTANCE']
    cycle_time = 0.1
    change = 100 - min_distance
    last_distance_val = scanner_distance.value(percent=True)
    last_time = time.time()
    while last_distance_val < min_distance:
        distance_val = scanner_distance.value(percent=True)
        if distance_val < min_distance * 0.65:
            return True

        change = abs(distance_val - last_distance_val) + change / 2
        last_distance_val = distance_val
        if change < 5:
            return False

        last_time = wait_to_cycle_time('DetectCollision', last_time, cycle_time)

    return False


def collision_avoid(shared: ShareAccessInterface, config: dict, pilot: Pilot, scanner_distance: Scanner):
    power_regulator = RangeRegulator(const_p=1, const_i=3, const_d=2,  # TODO: to config
                                     getter_target=lambda: config['OBSTACLE_MIN_DISTANCE'] * 0.8)

    cycle_time = 0.05  # TODO: to config
    wait_time = 2  # TODO: to config

    start_positions = pilot.get_positions()
    pilot.run_direct()

    last_time = time.time()
    while shared.should_run():
        distance_val = scanner_distance.value_scan(0, percent=True)
        power = power_regulator.regulate(distance_val) * -1
        pilot.update_duty_cycle(0, crop_m(power, max_out=0))

        if distance_val > power_regulator.target():
            pilot.stop()

            last_time = time.time()
            distance_val = scanner_distance.value_scan(0, percent=True)
            while distance_val > power_regulator.target():
                if not shared.should_run():
                    return

                if time.time() - last_time < wait_time:
                    time.sleep(cycle_time)
                else:
                    problem = False
                    if scanner_distance.motor_connected:
                        for i in [-1, 1]:
                            side_distance_val = scanner_distance.value_scan(40 * i, percent=True)

                            if side_distance_val < power_regulator.target():
                                scanner_distance.rotate_to_abs_pos(0)
                                problem = True

                    if problem:
                        continue

                    if scanner_distance.motor_connected:
                        scanner_distance.rotate_to_abs_pos(0)

                    target_speed = config['TARGET_POWER'] / 100 * pilot.get_max_speed_unit()
                    pilot.restore_positions(start_positions, speed_unit=target_speed)

                    distance_val = scanner_distance.value_scan(0, percent=True)
                    while distance_val > power_regulator.target():
                        if not shared.should_run():
                            return

                        if not pilot.is_running():
                            return
                        distance_val = scanner_distance.value_scan(0, percent=True)

                    pilot.stop()
                    break

                distance_val = scanner_distance.value_scan(0, percent=True)

            pilot.run_direct()
            last_time = time.time()

        last_time = wait_to_cycle_time(__name__, last_time, cycle_time)

    pilot.stop()
    if scanner_distance.motor_connected:
        scanner_distance.rotate_to_abs_pos(0)


def obstacle_avoid(shared: ShareAccessInterface, config: dict, robot_size: Size, pilot: Pilot,
                   scanner_distance: Scanner, scanner_reflect: Scanner):
    wait_time = 0.01

    line_info = shared.data.line_info
    min_reflect = line_info['min_reflect']
    max_reflect = line_info['max_reflect']  # TODO: use new method
    target_position = config['TARGET_POSITION']

    target_power = config['TARGET_POWER']
    target_speed = target_power / 100 * pilot.get_max_speed_unit()

    min_distance = config['OBSTACLE_MIN_DISTANCE'] + 10 + BRICK_SCANNER_DISTANCE_SENSOR.position.get(None).point.y
    obstacle_width = config['OBSTACLE_WIDTH']
    obstacle_height = config['OBSTACLE_HEIGHT']
    side = config['OBSTACLE_AVOID_SIDE']
    course = 80 * side
    scanner_pos = 90 * -side
    detect = obstacle_width == 0 or obstacle_height == 0
    if detect and not scanner_distance.motor_connected:
        log.warn('Can\'t avoid obstacle without obstacle_width and obstacle_height or rotating distance_sensor.')
        return

    pilot.run_percent_drive_to_angle_deg(90, course, speed_unit=target_speed)
    if detect:
        scanner_distance.rotate_to_abs_pos(scanner_pos)
    pilot.wait_to_stop()

    if detect:
        for i in range(2):
            pilot.run_percent_drive_forever(0, speed_unit=target_speed)
            while scanner_distance.value(percent=True) < min_distance:
                time.sleep(wait_time)
            pilot.run_percent_drive_to_angle_deg(90, -course, speed_unit=target_speed)
            pilot.wait_to_stop()
    else:
        pilot.run_percent_drive_to_distance((obstacle_width / 2) - (robot_size.width / 3), 0, speed_unit=target_speed)
        pilot.wait_to_stop()
        pilot.run_percent_drive_to_angle_deg(90, -course, speed_unit=target_speed)
        pilot.wait_to_stop()
        pilot.run_percent_drive_to_distance(obstacle_height, 0)
        pilot.wait_to_stop()
        pilot.run_percent_drive_to_angle_deg(90, -course, speed_unit=target_speed)
        pilot.wait_to_stop()

    pilot.run_percent_drive_forever(0, speed_unit=target_speed)
    if scanner_distance.motor_connected:
        scanner_distance.rotate_to_abs_pos(0)

    def get_reflect_percent():
        return (scanner_reflect.value(percent=False) - min_reflect) / (max_reflect - min_reflect) * 100

    while get_reflect_percent() > target_position:
        time.sleep(wait_time)

    pilot.run_percent_drive_forever(course, speed_unit=target_speed)

    while get_reflect_percent() <= target_position:
        time.sleep(wait_time)

    time.sleep(wait_time * 4)

    while get_reflect_percent() > target_position:
        time.sleep(wait_time)

    pilot.stop()


def run_loop(shared: ShareAccessInterface):
    runtime_config = shared.data.config
    config = runtime_config.extract_config_values(
        'TARGET_POSITION', 'TARGET_POWER', 'OBSTACLE_AVOID', 'OBSTACLE_AVOID_SIDE', 'OBSTACLE_MIN_DISTANCE',
        'OBSTACLE_WIDTH', 'OBSTACLE_HEIGHT', 'COLLISION_AVOID', 'TARGET_CYCLE_TIME'
    )

    robot_size = shared.data.robot_size
    pilot = shared.data.pilot
    scanner_distance = shared.data.scanner_distance
    scanner_reflect = shared.data.scanner_reflect

    if not scanner_distance.head_connected:
        return

    while shared.should_run():
        runtime_config.update_extracted_config(config)

        if (config['OBSTACLE_AVOID'] or config['COLLISION_AVOID']) \
                and (not scanner_distance.motor_connected or not scanner_distance.is_running):
            if scanner_distance.motor_connected and scanner_distance.angle_deg() != 0:
                scanner_distance.rotate_to_abs_pos(0)
                scanner_distance.wait_to_stop()
                continue

            if scanner_distance.value(percent=True) <= config['OBSTACLE_MIN_DISTANCE']:
                shared.request_pause(THREAD_LINE_FOLLOW_NAME, True)
                if config['COLLISION_AVOID'] and \
                        (not config['OBSTACLE_AVOID'] or detect_collision(config, scanner_distance)):
                    collision_avoid(shared, config, pilot, scanner_distance)
                else:
                    obstacle_avoid(shared, config, robot_size, pilot, scanner_distance, scanner_reflect)
                shared.request_resume(THREAD_LINE_FOLLOW_NAME)

        time.sleep(0.1)
