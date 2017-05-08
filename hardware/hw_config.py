import math
import sys

from utils.calc import dimensions as dp
from utils.calc.size import WheelSize, Size
from utils.hardware.brick.bricks import IN_3, IN_4, OUT_A, OUT_B, OUT_C, OUT_D
from utils.hardware.propulsion import ScannerPropulsionInfo
from utils.hardware.wheel import WheelInfo


class Simulation:
    enabled = '--simulate' in sys.argv
    show_gui = '--gui' in sys.argv


class Robot:
    size = Size(15, 23, 16, 0)  # TODO: measure weight
    center_pos_abs = dp.Position(dp.Point(0, -2.4, 0) if '--hw-fast' in sys.argv else dp.Point(0, 0, 0), dp.Angle())


class MainBrick:
    pos_abs = dp.Position(dp.Point(0, -3, 0), dp.Angle())


class WheelLeft:
    class Propulsion:
        port = OUT_B
        pos_abs = dp.Position(dp.Point(-2.4, 0, 0), dp.Angle(math.radians(90)))

    info = WheelInfo(
        dp.Position(dp.Point(-6, 0, 0), dp.Angle(math.radians(-90))),
        WheelSize(2.1, 4.3, 0), 360, -12 / 36 if '--hw-fast' in sys.argv else 1
    )


class WheelRight:
    class Propulsion:
        port = OUT_C
        pos_abs = dp.Position(dp.Point(2.4, 0, 0), dp.Angle(math.radians(90)))

    info = WheelInfo(
        dp.Position(dp.Point(6, 0, 0), dp.Angle(math.radians(90))),
        WheelSize(2.1, 4.3, 0), 360, -12 / 36 if '--hw-fast' in sys.argv else 1
    )


class ScannerDistance:
    class Propulsion:
        port = OUT_A
        pos_abs = dp.Position(dp.Point(0, 0, 0), dp.Angle())
        info = ScannerPropulsionInfo(-20 / 12, 360)

    class Head:
        port = IN_4
        pos_rel = dp.Position(dp.Point(0, 10.5, 0), dp.Angle())
        gear_rotation = dp.Angle()  # TODO: measure


class ScannerReflect:
    class Propulsion:
        port = OUT_D
        pos_abs = dp.Position(dp.Point(0, 5.5, 0), dp.Angle())
        info = ScannerPropulsionInfo(-20 / 12, 360)

    class Head:
        port = IN_3
        pos_rel = dp.Position(dp.Point(0, 4, 0), dp.Angle())
        gear_rotation = dp.Angle(rad_x=-90)


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

ScannerDistance.Propulsion.pos_abs.point.move(move)
ScannerDistance.Propulsion.pos_abs.angle.rotate(rotate)

ScannerReflect.Propulsion.pos_abs.point.move(move)
ScannerReflect.Propulsion.pos_abs.angle.rotate(rotate)
del move, rotate
