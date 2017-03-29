from utils.hardware.propulsion import ScannerPropulsion
from utils.hardware.sensor import SensorHeadMode


class Scanner:
    def __init__(self, scanner_propulsion: ScannerPropulsion, scanner_head: SensorHeadMode):
        self._scanner_propulsion = scanner_propulsion
        self._scanner_head = scanner_head

    @property
    def head(self):
        return self._scanner_head

    @property
    def propulsion(self):
        return self._scanner_propulsion

    def reset(self):
        self._scanner_head.reset()
        self._scanner_propulsion.reset()

    def rotate_to_pos(self, angle, speed=None):
        self._scanner_propulsion.rotate_to_pos(angle, speed)

    @property
    def head_connected(self):
        return self._scanner_head.connected

    @property
    def motor_connected(self):
        return self._scanner_propulsion.connected

    @property
    def is_running(self):
        return self._scanner_propulsion.is_running

    @property
    def value_max(self):
        return self._scanner_head.value_range.val_max

    def repeat_while_running(self, method):
        self._scanner_propulsion.repeat_while_running(method)

    def wait_to_stop(self):
        self._scanner_propulsion.wait_to_stop()

    def value(self, percent=True, n=0):
        return self._scanner_head.value(percent, n)

    def values(self, percent=True):
        return self._scanner_head.values(percent)

    def angle_deg(self):
        return self._scanner_propulsion.angle_deg

    def value_scan(self, angle=0, percent=True, n=0):
        if self.motor_connected:
            if self.angle_deg != angle:
                self.rotate_to_pos(angle)
                self.wait_to_stop()
        elif angle != 0:
            raise Exception('Scanner motor is not connected')
        return self.value(percent, n)

    def value_scan_continuous(self, to_angle, value_handler, percent=True, n=0):
        self.rotate_to_pos(to_angle)
        self.repeat_while_running(lambda: value_handler(self.value(percent, n), self.angle_deg))
