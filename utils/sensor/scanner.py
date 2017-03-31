from utils.hardware.propulsion import ScannerPropulsion
from utils.hardware.sensor import SensorHeadMode


class Scanner:
    def __init__(self, propulsion: ScannerPropulsion, head: SensorHeadMode):
        self._propulsion = propulsion
        self._head = head

    @property
    def head(self):
        return self._head

    @property
    def propulsion(self):
        return self._propulsion

    def reset(self):
        self._head.reset()
        self._propulsion.reset()

    def rotate_to_pos(self, angle, speed=None):
        self._propulsion.rotate_to_pos(angle, speed)

    @property
    def head_connected(self):
        return self._head.connected

    @property
    def motor_connected(self):
        return self._propulsion.connected

    @property
    def is_running(self):
        return self._propulsion.is_running

    @property
    def value_max(self):
        return self._head.value_range.val_max

    def repeat_while_running(self, method):
        self._propulsion.repeat_while_running(method)

    def wait_to_stop(self):
        self._propulsion.wait_to_stop()

    def value(self, percent=False, n=0):
        return self._head.value(percent, n)

    def values(self, percent=False):
        return self._head.values(percent)

    def angle_deg(self):
        return self._propulsion.angle_deg

    def value_scan(self, angle=0, percent=False, n=0):
        if self.motor_connected:
            if self.angle_deg != angle:
                self.rotate_to_pos(angle)
                self.wait_to_stop()
        elif angle != 0:
            raise Exception('Scanner motor is not connected')
        return self.value(percent, n)

    def value_scan_continuous(self, to_angle, value_handler, percent=False, n=0):
        self.rotate_to_pos(to_angle)
        self.repeat_while_running(lambda: value_handler(self.value(percent, n), self.angle_deg))

    def generate_json_info(self):
        return {
            'propulsion': self.propulsion.generate_json_info(),
            'head': self.head.generate_json_info()
        }
