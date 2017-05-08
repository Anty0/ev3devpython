from hardware.generator import HW_GENERATOR

pilot = HW_GENERATOR.pilot()

try:
    print('Running...')
    pilot.reset()

    # PILOT.run_percent_drive_to_distance(15, 0, 3)
    # PILOT.wait_to_stop()
    # time.sleep(2)
    pilot.run_percent_drive_to_angle_deg(360 * 15, 200, speed_mul=0.5)
    pilot.wait_to_stop()
finally:
    pilot.stop()
