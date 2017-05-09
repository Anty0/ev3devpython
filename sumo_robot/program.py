import time


def run():
    from sumo_robot.hardware.generator import HW_GENERATOR
    pilot = HW_GENERATOR.pilot()
    pilot.reset()
    time.sleep(10)

    pilot.run_drive_to_distance(150, 0, speed_unit=1)
    pilot.wait_to_stop()
    time.sleep(5)
    pilot.run_percent_drive_to_angle_deg(360 * 3, 200, speed_mul=0.3)
    pilot.wait_to_stop()
    time.sleep(10)
