#!/usr/bin/env python3
from ev3dev.auto import *

left_motor = LargeMotor(OUTPUT_A)
right_motor = LargeMotor(OUTPUT_D)

time.sleep(5)

left_motor.run_direct()
right_motor.run_direct()

left_motor.duty_cycle_sp = -100
right_motor.duty_cycle_sp = -100

try:
    while True:
        time.sleep(10)
finally:
    left_motor.stop()
    right_motor.stop()
