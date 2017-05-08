import math

from ev3dev.auto import Motor

from utils.calc import dimensions as dp
from utils.calc.size import WheelSize


class WheelInfo:
    def __init__(self, position: dp.Position, size: WheelSize, count_per_rot: int, gear_ratio: float):
        self.position = position  # FIXME: fix position usages
        self.size = size

        self.gear_ratio = gear_ratio
        self.motor_tacho_ratio = count_per_rot / 360
        self.total_ratio = self.gear_ratio * self.motor_tacho_ratio
        self.unit_ratio = 360 / (math.pi * self.size.diameter)
        self.unit_ratio_rad = math.radians(360) / (math.pi * self.size.diameter)


class Wheel:
    def __init__(self, motor: Motor, info: WheelInfo):  # FIXME: remove old usages of non info values
        self.motor = motor
        self.info = info
        self.diameter = info.size.diameter
        self.width = info.size.width

        self.offset = info.position.point.x
        self.offset_position = info.position

        self.gear_ratio = info.gear_ratio
        self.motor_tacho_ratio = info.motor_tacho_ratio
        self.total_ratio = info.total_ratio
        self.unit_ratio = info.unit_ratio

    def generate_json_info(self):
        return {
            'motor': {
                'connected': self.motor.connected,
                'position': self.motor.position if self.motor.connected else 'unavailable',
                'speed': self.motor.speed if self.motor.connected else 'unavailable',
                'running': (Motor.STATE_RUNNING in self.motor.state) if self.motor.connected else 'unavailable'
            },
            'diameter': self.diameter,
            'width': self.width,
            'offset_y': self.offset,
            'gear_ratio': self.gear_ratio,
            'motor_tacho_ratio': self.motor_tacho_ratio,
            'total_ratio': self.total_ratio,
            'unit_ratio': self.unit_ratio
        }
