import time

# from hardware.wheels import LEFT_MOTOR, RIGHT_MOTOR
from hardware.pilot import PILOT
# from utils.calc.range import Range
from utils.control.odometry import OdometryCalculatorThread, PositionsCollector
from utils.graph import graph_to_string, GraphPoint

odometry = OdometryCalculatorThread(*PILOT.wheels)
position_collector = PositionsCollector(odometry, 0.02)


def print_positions():
    print(graph_to_string('Positions', [GraphPoint(point[0], point[1]) for point in position_collector.positions]))
    # 80, 40))  # , Range(-7, 7), Range(-14, 1)))


try:
    print('Running...')

    PILOT.reset()
    odometry.start()
    position_collector.start()


    # LEFT_MOTOR.run_to_rel_pos(position_sp=360, speed_sp=50)
    # while LEFT_MOTOR.STATE_RUNNING in LEFT_MOTOR.state:
    #     time.sleep(0.5)
    #
    # RIGHT_MOTOR.run_to_rel_pos(position_sp=-360, speed_sp=50)
    # while RIGHT_MOTOR.STATE_RUNNING in RIGHT_MOTOR.state:
    #     time.sleep(0.5)

    def wait_to_stop():
        PILOT.wait_to_stop()
        # while PILOT.is_running():
        #     print_positions()
        #     time.sleep(0.5)
        # time.sleep(0.5)
        # print_positions()
        time.sleep(1.5)


    PILOT.run_percent_drive_to_distance(25, 0, speed_mul=0.1)
    wait_to_stop()
    PILOT.run_percent_drive_to_angle_deg(90, 100, speed_mul=0.1)
    wait_to_stop()
    PILOT.run_percent_drive_to_angle_deg(90, 150, speed_mul=0.1)
    wait_to_stop()
    PILOT.run_percent_drive_to_distance(25, 0, speed_mul=0.1)
    wait_to_stop()
finally:
    PILOT.stop()
    odometry.stop()
    odometry.wait_to_stop()
    position_collector.stop()
    position_collector.wait_to_stop()
    print_positions()
