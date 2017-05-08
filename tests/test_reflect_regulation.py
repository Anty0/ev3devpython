import time

from hardware.brick_scanner_reflect import BRICK_SCANNER_REFLECT
from hardware.generator import HW_GENERATOR
from utils.calc.regulator import RangeRegulator
from utils.utils import wait_to_cycle_time, crop_r

MIN_REFLECT = 3  # 7
MAX_REFLECT = 25  # 63
CYCLE_TIME = 0.02

regulator = RangeRegulator(const_p=0.3, const_i=0, const_d=0.275, const_target=55)

pilot = HW_GENERATOR.pilot()
scanner_reflect = HW_GENERATOR.scanner(BRICK_SCANNER_REFLECT)
scanner_motor = scanner_reflect.propulsion.motor
scanner_motor_gear_ratio = scanner_reflect.propulsion.propulsion_info.total_ratio
scanner_sensor = scanner_reflect.head.sensor

try:
    print('Running...')

    pilot.reset()
    scanner_sensor.mode = scanner_sensor.MODE_COL_REFLECT
    scanner_motor.stop_action = scanner_motor.STOP_ACTION_BRAKE
    scanner_motor.run_direct(duty_cycle_sp=0)
    pilot.run_direct()

    last_time = time.time()
    while True:
        input_raw = scanner_sensor.value()
        input_percent = (input_raw - MIN_REFLECT) / (MAX_REFLECT - MIN_REFLECT) * 100
        course = regulator.regulate(input_percent)
        scanner_motor.duty_cycle_sp = crop_r(course)

        angle = scanner_motor.position / scanner_motor_gear_ratio
        pilot.update_duty_cycle_unit(0, target_duty_cycle=10)

        last_time = wait_to_cycle_time('SensorPosRegulation', last_time, CYCLE_TIME)
finally:
    pilot.stop()
    scanner_motor.stop()
    scanner_motor.run_to_abs_pos(position_sp=0, speed_sp=50)
