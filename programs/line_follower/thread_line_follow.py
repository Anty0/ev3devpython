import time

from utils.calc.regulator import PercentRegulator
from utils.log import get_logger
from utils.threading.co_working_threads import ShareAccessInterface
from utils.utils import wait_to_cycle_time, crop_r

log = get_logger(__name__)


def run_loop(shared: ShareAccessInterface):
    runtime_config = shared.data.config
    config = runtime_config.extract_config_values(
        'REG_STEER_P', 'REG_STEER_I', 'REG_STEER_D', 'PAUSE_POWER',
        'TARGET_POWER', 'TARGET_REFLECT', 'LINE_SIDE', 'TARGET_CYCLE_TIME'
    )
    detect_reflect = runtime_config.get_config_value('DETECT_REFLECT')
    min_reflect = runtime_config.get_config_value('MIN_REFLECT')
    max_reflect = runtime_config.get_config_value('MAX_REFLECT')
    min_to_max_distance = runtime_config.get_config_value('MIN_TO_MAX_DISTANCE')

    pilot = shared.data.pilot
    scanner_reflect = shared.data.scanner_reflect

    if detect_reflect:
        if scanner_reflect.motor_connected:
            scanner_reflect.rotate_to_pos(0)
            scanner_reflect.wait_to_stop()

        results = []
        scans = []

        def scan_reflect():
            read = scanner_reflect.value(False)
            positions = pilot.get_positions()
            scans.append([read, positions])

        pilot.run_percent_drive_to_angle_deg(45, 200, speed_mul=0.15)
        pilot.wait_to_stop()

        pilot.run_percent_drive_to_angle_deg(90, -200, speed_mul=0.05)
        pilot.repeat_while_running(scan_reflect)

        pilot.run_percent_drive_to_angle_deg(45, 200, speed_mul=0.15)
        pilot.wait_to_stop()

        pilot.run_percent_drive_to_distance(1, 0, speed_mul=-0.1)
        results.append(scans)
        scans = []
        pilot.wait_to_stop()

        pilot.run_percent_drive_to_angle_deg(45, 200, speed_mul=0.15)
        pilot.wait_to_stop()

        pilot.run_percent_drive_to_angle_deg(90, -200, speed_mul=0.05)
        pilot.repeat_while_running(scan_reflect)

        pilot.run_percent_drive_to_angle_deg(45, 200, speed_mul=0.15)
        pilot.wait_to_stop()

        results.append(scans)
        del scans

        # TODO: process results

        # log.debug('Scan results ' + str(reflect))
        # if reflect[0] == reflect[1]:
        #     log.error('Failed to detect reflect, falling back to defaults.')
        # else:
        #     min_reflect = reflect[0]
        #     max_reflect = reflect[1]

    regulator_steer = PercentRegulator(getter_p=lambda: config['REG_STEER_P'],
                                       getter_i=lambda: config['REG_STEER_I'],
                                       getter_d=lambda: config['REG_STEER_D'],
                                       getter_target=lambda: config['TARGET_REFLECT'])

    regulator_sensor = None  # TODO: create, rework and and test

    def reset_regulation():
        regulator_steer.reset()

    config.add_on_config_whole_change_listener(reset_regulation)
    val_change_listner = lambda name, new_value: reset_regulation() if name.startswith('REG_STEER') else None
    config.add_on_config_value_change_listener(val_change_listner)

    try:
        pilot.run_direct()
        last_time = time.time()
        while shared.should_run():
            runtime_config.update_extracted_config(config)

            read_val = scanner_reflect.value(False)
            read_percent = 100 * (read_val - min_reflect) / (max_reflect - min_reflect)
            course = crop_r(regulator_steer.regulate(read_percent) * config['LINE_SIDE'])

            pilot.update_duty_cycle(course, mul_duty_cycle=config['TARGET_POWER'] / 100)

            if shared.should_pause():
                pilot.stop()

                shared.wait_resume()

                reset_regulation()
                pilot.run_direct()
                last_time = time.time()

            last_time = wait_to_cycle_time('line_follow', last_time, config['TARGET_CYCLE_TIME'])
    finally:
        pilot.stop()
        config.remove_on_config_whole_change_listener(reset_regulation)
        config.remove_on_config_value_change_listener(val_change_listner)
