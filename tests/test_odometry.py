import time

from hardware.generator import HW_GENERATOR
from utils.control.odometry import PositionsCollector, from_wheels
from utils.graph import graph_to_string, GraphPoint
from utils.threading.cycle_thread import CycleThread

pilot = HW_GENERATOR.pilot()
odometry = from_wheels(*pilot.wheels)
odometry_thread = CycleThread(target=odometry.cycle, sleep_time=0.02, daemon=True)
position_collector = PositionsCollector(odometry)
position_collector_thread = CycleThread(target=position_collector.cycle, sleep_time=0.02, daemon=True)


def print_positions():
    print(graph_to_string('Positions', [GraphPoint(point[0], point[1]) for point in position_collector.positions]))
    # 80, 40))  # , Range(-7, 7), Range(-14, 1)))


try:
    print('Running...')

    pilot.reset()
    odometry_thread.start()
    position_collector_thread.start()

    # LEFT_MOTOR.run_to_rel_pos(position_sp=360, speed_sp=50)
    # while LEFT_MOTOR.STATE_RUNNING in LEFT_MOTOR.state:
    #     time.sleep(0.5)
    #
    # RIGHT_MOTOR.run_to_rel_pos(position_sp=-360, speed_sp=50)
    # while RIGHT_MOTOR.STATE_RUNNING in RIGHT_MOTOR.state:
    #     time.sleep(0.5)

    def wait_to_stop():
        pilot.wait_to_stop()
        # while pilot.is_running():
        #     print_positions()
        #     time.sleep(0.5)
        # time.sleep(0.5)
        # print_positions()
        time.sleep(1.5)


    pilot.run_percent_drive_to_distance(25, 0, speed_mul=0.1)
    wait_to_stop()
    pilot.run_percent_drive_to_angle_deg(90, 100, speed_mul=0.1)
    wait_to_stop()
    pilot.run_percent_drive_to_angle_deg(90, 150, speed_mul=0.1)
    wait_to_stop()
    pilot.run_percent_drive_to_distance(25, 0, speed_mul=0.1)
    wait_to_stop()
finally:
    pilot.stop()
    odometry_thread.stop()
    odometry_thread.wait_to_stop()
    position_collector_thread.stop()
    position_collector_thread.wait_to_stop()
    print_positions()
