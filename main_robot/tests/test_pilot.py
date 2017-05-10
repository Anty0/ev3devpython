import time

from main_robot.hardware.generator import HW_GENERATOR
from main_robot.hardware.gui import show as show_gui
from main_robot.hardware.hw_config import Robot

show_gui()

pilot = HW_GENERATOR.pilot()
target_speed = 70 / 100 * pilot.get_max_speed_unit()

try:
    print('Running...')
    pilot.reset()

    pilot.run_percent_drive_to_angle_deg(90, -80, speed_unit=target_speed)
    pilot.wait_to_stop()
    pilot.run_percent_drive_to_distance((15 / 2) - (Robot.size.width / 3), 0, speed_unit=70)
    pilot.wait_to_stop()
    pilot.run_percent_drive_to_angle_deg(90, 80, speed_unit=target_speed)
    pilot.wait_to_stop()
    pilot.run_percent_drive_to_distance(15, 0)
    pilot.wait_to_stop()
    pilot.run_percent_drive_to_angle_deg(90, 80, speed_unit=target_speed)
    pilot.wait_to_stop()

    # time.sleep(10)
    # pilot.run_percent_drive_to_distance(15, 0, speed_unit=5)
    # pilot.wait_to_stop()
    # time.sleep(5)
    # pilot.run_percent_drive_to_angle_deg(90, 100, speed_unit=1)
    # pilot.wait_to_stop()
    # time.sleep(5)
    # pilot.run_percent_drive_to_angle_deg(90, -200, speed_mul=0.5)
    # pilot.wait_to_stop()
finally:
    pilot.stop()
    time.sleep(15)
