import time

from utils.calc.regulator import PercentRegulator
from utils.log import get_logger
from utils.threading.co_working_threads import ShareAccessInterface
from utils.utils import wait_to_cycle_time, crop_r

log = get_logger(__name__)


def run_loop(shared: ShareAccessInterface):
    pilot = shared.data.pilot
    scanner_reflect = shared.data.scanner_reflect

    runtime_config = shared.data.config
    config = runtime_config.extract_config_values(
        'REG_STEER_P', 'REG_STEER_I', 'REG_STEER_D',
        'TARGET_POWER', 'TARGET_REFLECT', 'LINE_SIDE', 'TARGET_CYCLE_TIME'
    )
    detect_reflect = runtime_config.get_config_value('DETECT_REFLECT')
    min_reflect = runtime_config.get_config_value('MIN_REFLECT')
    max_reflect = runtime_config.get_config_value('MAX_REFLECT')
    min_to_max_distance = runtime_config.get_config_value('MIN_TO_MAX_DISTANCE')

    if detect_reflect:
        if scanner_reflect.motor_connected:
            scanner_reflect.rotate_to_pos(0)
            scanner_reflect.wait_to_stop()

        scan_results = {'scan0': {}, 'scan1': {}}
        scan_tmp = []

        def scan_reflect():
            read = scanner_reflect.value(percent=False)
            positions = pilot.get_positions()
            scan_tmp.append([read, positions])

        scan_results['scan0']['startPosition'] = pilot.get_positions()

        pilot.run_percent_drive_to_angle_deg(45, 200, speed_mul=0.15)
        pilot.wait_to_stop()

        pilot.run_percent_drive_to_angle_deg(90, -200, speed_mul=0.05)
        pilot.repeat_while_running(scan_reflect)

        pilot.run_percent_drive_to_angle_deg(45, 200, speed_mul=0.15)
        pilot.wait_to_stop()

        pilot.run_percent_drive_to_distance(1, 0, speed_mul=-0.1)
        scan_results['scan0']['results'] = scan_tmp
        scan_tmp = []
        pilot.wait_to_stop()

        scan_results['scan1']['startPosition'] = pilot.get_positions()

        pilot.run_percent_drive_to_angle_deg(45, 200, speed_mul=0.15)
        pilot.wait_to_stop()

        pilot.run_percent_drive_to_angle_deg(90, -200, speed_mul=0.05)
        pilot.repeat_while_running(scan_reflect)

        pilot.run_percent_drive_to_angle_deg(45, 200, speed_mul=0.15)
        pilot.wait_to_stop()

        scan_results['scan1']['results'] = scan_tmp
        del scan_tmp

        # TODO: process results

        for scan in scan_results.keys():
            start_position = scan_results[scan]['startPosition']
            start_position_len = len(start_position)
            for result in scan_results[scan]['results']:
                position = result[1]
                result.append(pilot.positions_change_to_angle
                              ([position[i] - start_position[i] for i in range(start_position_len)]))

        for scan in scan_results.keys():
            shared.data.add_new_graph({
                'name': 'Reflect ' + scan,
                'labels': [result[2] for result in scan_results[scan]['results']],
                'data': [result[0] for result in scan_results[scan]['results']]
            })

        # log.debug('Scan results ' + str(reflect))
        # if reflect[0] == reflect[1]:
        #     log.error('Failed to detect reflect, falling back to defaults.')
        # else:
        #     min_reflect = reflect[0]
        #     max_reflect = reflect[1]

        del scan_results

    shared.data.min_reflect = min_reflect
    shared.data.max_reflect = max_reflect
    shared.data.min_to_max_distance = min_to_max_distance

    regulator_steer = PercentRegulator(getter_p=lambda: config['REG_STEER_P'],
                                       getter_i=lambda: config['REG_STEER_I'],
                                       getter_d=lambda: config['REG_STEER_D'],
                                       getter_target=lambda: config['TARGET_REFLECT'])

    regulator_sensor = None  # TODO: create, rework and and test

    try:
        pilot.run_direct()
        last_time = time.time()
        while shared.should_run():
            if runtime_config.update_extracted_config(config):
                regulator_steer.reset()

            read_val = scanner_reflect.value(percent=False)
            read_percent = 100 * (read_val - min_reflect) / (max_reflect - min_reflect)
            course = crop_r(regulator_steer.regulate(read_percent) * config['LINE_SIDE'])

            if shared.data.pause:
                pilot.update_duty_cycle(course, target_duty_cycle=0, mul_duty_cycle=config['TARGET_POWER'] / 100)
            else:
                pilot.update_duty_cycle(course, mul_duty_cycle=config['TARGET_POWER'] / 100)

            if shared.should_pause():
                pilot.stop()

                shared.wait_resume()

                regulator_steer.reset()
                pilot.run_direct()
                last_time = time.time()

            last_time = wait_to_cycle_time('line_follow', last_time, config['TARGET_CYCLE_TIME'])
    finally:
        pilot.stop()
