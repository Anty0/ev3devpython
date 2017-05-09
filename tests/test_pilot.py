import time

from hardware.generator import HW_GENERATOR
from hardware.gui import show as show_gui

show_gui()

pilot = HW_GENERATOR.pilot()

try:
    print('Running...')
    pilot.reset()

    time.sleep(10)
    pilot.run_percent_drive_to_distance(80, 0, speed_unit=5)
    pilot.wait_to_stop()
    time.sleep(5)
    pilot.run_percent_drive_to_angle_deg(90, 20, speed_unit=1)
    pilot.wait_to_stop()
    time.sleep(5)
    pilot.run_percent_drive_to_angle_deg(90, -200, speed_mul=0.5)
    pilot.wait_to_stop()
finally:
    pilot.stop()
    time.sleep(15)
