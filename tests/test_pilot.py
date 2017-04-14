from hardware.pilot import PILOT

try:
    print('Running...')
    PILOT.reset()

    # PILOT.run_percent_drive_to_distance(15, 0, 3)
    # PILOT.wait_to_stop()
    # time.sleep(2)
    PILOT.run_percent_drive_to_angle_deg(360 * 15, 200, speed_mul=0.5)
    PILOT.wait_to_stop()
finally:
    PILOT.stop()
