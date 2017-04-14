import time

from hardware.pilot import PILOT
from hardware.scanner_reflect import SCANNER_REFLECT_PROPULSION_MOTOR as MOTOR, \
    SCANNER_REFLECT_PROPULSION_GEAR_RATIO as MOTOR_GEAR_RATIO
from hardware.sensor_color import SENSOR_COLOR as SENSOR
from utils.calc.regulator import RangeRegulator
from utils.utils import wait_to_cycle_time, crop_r

MIN_REFLECT = 3  # 7
MAX_REFLECT = 25  # 63
CYCLE_TIME = 0.02

regulator = RangeRegulator(const_p=0.3, const_i=0, const_d=0.275, const_target=55)

try:
    print('Running...')

    PILOT.reset()
    SENSOR.mode = SENSOR.MODE_COL_REFLECT
    MOTOR.stop_action = MOTOR.STOP_ACTION_BRAKE
    MOTOR.run_direct(duty_cycle_sp=0)
    PILOT.run_direct()

    last_time = time.time()
    while True:
        input_raw = SENSOR.value()
        input_percent = (input_raw - MIN_REFLECT) / (MAX_REFLECT - MIN_REFLECT) * 100
        course = regulator.regulate(input_percent)
        MOTOR.duty_cycle_sp = crop_r(course)

        angle = MOTOR.position / MOTOR_GEAR_RATIO
        PILOT.update_duty_cycle_unit(0, target_duty_cycle=10)

        last_time = wait_to_cycle_time('SensorPosRegulation', last_time, CYCLE_TIME)
finally:
    PILOT.stop()
    MOTOR.stop()
    MOTOR.run_to_abs_pos(position_sp=0, speed_sp=50)
