import math
import sys

from utils.calc import dimensions as dp
from utils.calc.size import WheelSize, Size
from utils.hardware.brick.bricks import IN_1, OUT_A, OUT_D
from utils.hardware.wheel import WheelInfo


class Simulation:
    enabled = '--simulate' in sys.argv
    show_gui = '--gui' in sys.argv


class Robot:
    size = Size(15, 23, 16, 0)  # TODO: measure weight and size
    center_pos_abs = dp.Position(dp.Point(0, 0, 0), dp.Angle())


class MainBrick:
    pos_abs = dp.Position(dp.Point(0, -3, 0), dp.Angle())  # TODO: measure position


class WheelLeft:
    class Propulsion:
        port = OUT_A
        pos_abs = dp.Position(dp.Point(-2.4, 0, 0), dp.Angle(math.radians(90)))  # TODO: measure position

    info = WheelInfo(
        dp.Position(dp.Point(-6.5, 0, 0), dp.Angle(math.radians(-90))),
        WheelSize(2.8, 5.6, 0), 360, 1
    )


class WheelRight:
    class Propulsion:
        port = OUT_D
        pos_abs = dp.Position(dp.Point(2.4, 0, 0), dp.Angle(math.radians(90)))  # TODO: measure position

    info = WheelInfo(
        dp.Position(dp.Point(6.5, 0, 0), dp.Angle(math.radians(90))),
        WheelSize(2.8, 5.6, 0), 360, 1
    )


class ScannerDistance:
    class Head:
        port = IN_1
        pos_abs = dp.Position(dp.Point(0, 0, 0), dp.Angle(rad_x=math.radians(10)))


# Apply robot center offset
rotate = Robot.center_pos_abs.angle.copy().negate()
move = Robot.center_pos_abs.point.copy().negate()

Robot.center_pos_abs.point.move(move)
Robot.center_pos_abs.angle.rotate(rotate)

MainBrick.pos_abs.point.move(move)
MainBrick.pos_abs.angle.rotate(rotate)

# WheelLeft.Propulsion.pos_abs.angle.move(move)
# WheelLeft.Propulsion.pos_abs.point.rotate(rotate)
# WheelLeft.info.position.angle.move(move)
# WheelLeft.info.position.point.rotate(rotate)

# WheelRight.Propulsion.pos_abs.angle.move(move)
# WheelRight.Propulsion.pos_abs.point.rotate(rotate)
# WheelRight.info.position.angle.move(move)
# WheelRight.info.position.point.rotate(rotate)

ScannerDistance.Head.pos_abs.point.move(move)
ScannerDistance.Head.pos_abs.angle.rotate(rotate)
del move, rotate
