from ev3dev.auto import Sensor, InfraredSensor, UltrasonicSensor, ColorSensor

from utils.calc.range import Range


class SensorHeadMode:
    def __init__(self, sensor: Sensor, mode_name: str, value_range: Range):
        self._sensor = sensor
        self._mode_name = mode_name
        self._value_range = value_range

    def reset(self):
        if not self.connected:
            return
        self._sensor.mode = self._mode_name

    @property
    def sensor(self):
        return self._sensor

    @property
    def connected(self):
        return self._sensor and self._sensor.connected

    @property
    def mode_name(self):
        return self._mode_name

    @property
    def value_range(self):
        return self._value_range

    def _process_value(self, value, percent, n):
        return value if not percent else self._value_range.to_percent(value)

    def value(self, percent=False, n=0):
        return self._process_value(self._sensor.value(n), percent, n)

    def values(self, percent):
        return [self.value(percent, n) for n in range(self._sensor.num_values)]


class SensorHeadDistanceMode(SensorHeadMode):
    def __init__(self, ir_sensor: InfraredSensor = None, ultrasonic_sensor: UltrasonicSensor = None):
        if ir_sensor is None and ultrasonic_sensor is None:
            ir_sensor = InfraredSensor()
            ultrasonic_sensor = UltrasonicSensor()

        if ultrasonic_sensor.connected:
            mode_name = UltrasonicSensor.MODE_US_DIST_CM
            sensor = ultrasonic_sensor
            to_unit_mul = 1 if ultrasonic_sensor.driver_name is not 'lego-ev3-us' else 0.1
            min_value = 0
            max_value = 255 if ultrasonic_sensor.driver_name is not 'lego-ev3-us' else 2550
            max_value *= to_unit_mul
        elif ir_sensor.connected:
            mode_name = InfraredSensor.MODE_IR_PROX
            sensor = ir_sensor
            to_unit_mul = 0.7
            min_value = 0
            max_value = 100 * to_unit_mul
        else:
            mode_name = 'unknown'
            sensor = None
            to_unit_mul = 0
            min_value = 0
            max_value = 100

        self._to_unit_mul = to_unit_mul
        super().__init__(sensor, mode_name, Range(min_value, max_value))

    def _process_value(self, value, percent, n):
        return super()._process_value(value * self._to_unit_mul, percent, n)


class SensorHeadReflectMode(SensorHeadMode):
    def __init__(self, sensor: ColorSensor = None):
        if sensor is None:
            sensor = ColorSensor()
        super().__init__(sensor, ColorSensor.MODE_COL_REFLECT, Range(0, 100))
