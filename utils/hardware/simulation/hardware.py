import fnmatch
import time

from ev3dev.auto import Device, Motor, LargeMotor, MediumMotor, \
    Sensor, TouchSensor, ColorSensor, UltrasonicSensor, GyroSensor, InfraredSensor, SoundSensor, LightSensor

from utils.hardware.simulation.simulator import EnvironmentSimulator


class SimAttribute:
    def __init__(self, attr_name, device):
        self._attr_name = attr_name
        self._device = device

    def get_attr_name(self):
        return self._attr_name

    def seek(self, some_useless_param):
        pass

    def read(self) -> bytes:
        return str(getattr(self._device, self._attr_name)).encode()

    def write(self, text_input: bytes):
        setattr(self._device, self._attr_name, text_input.decode())

    def flush(self):
        pass


def list_sim_device_names(env_sim: EnvironmentSimulator, class_name, name_pattern, **kwargs):
    environment = env_sim.environment
    if class_name not in environment:
        return

    environment_class = environment[class_name]

    def matches(name, attr_name, pattern):
        try:
            value = getattr(environment_class[name], attr_name)
        except:
            return False

        if isinstance(pattern, list):
            return any([value.find(p) >= 0 for p in pattern])
        else:
            return value.find(pattern) >= 0

    for device_name in environment_class.keys():
        if fnmatch.fnmatch(device_name, name_pattern):
            if all([matches(device_name, k, kwargs[k]) for k in kwargs]):
                yield device_name


class SimDevice(Device):
    DRIVER_NAMES = ['unknown']

    def __init__(self, env_sim: EnvironmentSimulator, class_name, name_pattern='*', name_exact=False, **kwargs):
        Device.__init__(self, class_name, name_pattern, name_exact, **kwargs)

        def get_index(file):
            match = Device._DEVICE_INDEX.match(file)
            if match:
                return int(match.group('idx'))
            else:
                return None

        environment = env_sim.environment
        if name_exact:
            self._path = '/' + class_name + '/' + name_pattern
            self._device = environment[class_name][name_pattern]
            self._device_index = get_index(name_pattern)
            self.connected = True
        else:
            try:
                name = next(list_sim_device_names(env_sim, class_name, name_pattern, **kwargs))
                self._path = '/' + class_name + '/' + name_pattern
                self._device = environment[class_name][name]
                self._device_index = get_index(name)
                self.connected = True
            except StopIteration:
                self._path = None
                self._device_index = None
                self.connected = False

    def _attribute_file_open(self, name):
        return SimAttribute(name, self._device)


def list_sim_devices(sim_environment, class_name, name_pattern, **kwargs):
    return (SimDevice(sim_environment, class_name, name, name_exact=True)
            for name in list_sim_device_names(sim_environment, class_name, name_pattern, **kwargs))


class SimMotor(SimDevice, Motor):
    DRIVER_NAMES = ['lego-motor']

    def __init__(self, env_sim: EnvironmentSimulator, address=None, name_pattern=Motor.SYSTEM_DEVICE_NAME_CONVENTION,
                 name_exact=False, **kwargs):
        Motor.__init__(self, address, name_pattern, name_exact, **kwargs)
        if address is not None:
            kwargs['address'] = address
        SimDevice.__init__(self, env_sim, self.SYSTEM_CLASS_NAME, name_pattern, name_exact, **kwargs)

    @property
    def position_p(self):
        raise Exception('Unsupported by simulator.')

    @position_p.setter
    def position_p(self, value):
        raise Exception('Unsupported by simulator.')

    @property
    def position_i(self):
        raise Exception('Unsupported by simulator.')

    @position_i.setter
    def position_i(self, value):
        raise Exception('Unsupported by simulator.')

    @property
    def position_d(self):
        raise Exception('Unsupported by simulator.')

    @position_d.setter
    def position_d(self, value):
        raise Exception('Unsupported by simulator.')

    @property
    def speed_p(self):
        raise Exception('Unsupported by simulator.')

    @speed_p.setter
    def speed_p(self, value):
        raise Exception('Unsupported by simulator.')

    @property
    def speed_i(self):
        raise Exception('Unsupported by simulator.')

    @speed_i.setter
    def speed_i(self, value):
        raise Exception('Unsupported by simulator.')

    @property
    def speed_d(self):
        raise Exception('Unsupported by simulator.')

    @speed_d.setter
    def speed_d(self, value):
        raise Exception('Unsupported by simulator.')

    def wait(self, cond, timeout=None):
        start_time = time.time()
        while True:
            if timeout is not None and time.time() >= start_time + timeout / 1000:
                return False

            if cond(self.state):
                return True

            time.sleep(0.05)


def list_sim_motors(sim_environment, name_pattern=Motor.SYSTEM_DEVICE_NAME_CONVENTION, **kwargs):
    return (SimMotor(sim_environment, name_pattern=name, name_exact=True)
            for name in list_sim_device_names(sim_environment, Motor.SYSTEM_CLASS_NAME, name_pattern, **kwargs))


class SimLargeMotor(SimMotor, LargeMotor):
    DRIVER_NAMES = ['lego-ev3-l-motor', 'lego-nxt-motor']

    def __init__(self, env_sim: EnvironmentSimulator, address=None,
                 name_pattern=LargeMotor.SYSTEM_DEVICE_NAME_CONVENTION, name_exact=False, **kwargs):
        LargeMotor.__init__(self, address, name_pattern, name_exact, **kwargs)
        SimMotor.__init__(self, env_sim, address, name_pattern, name_exact,
                          driver_name=self.DRIVER_NAMES, **kwargs)


class SimMediumMotor(SimMotor, MediumMotor):
    DRIVER_NAMES = ['lego-ev3-m-motor']

    def __init__(self, env_sim: EnvironmentSimulator, address=None,
                 name_pattern=MediumMotor.SYSTEM_DEVICE_NAME_CONVENTION,
                 name_exact=False, **kwargs):
        MediumMotor.__init__(self, address, name_pattern, name_exact, **kwargs)
        SimMotor.__init__(self, env_sim, address, name_pattern, name_exact,
                          driver_name=self.DRIVER_NAMES, **kwargs)


class SimActuonixL1250Motor:  # placeholder
    pass  # TODO: add support


class SimActuonixL12100Motor:  # placeholder
    pass  # TODO: add support


class SimDcMotor:  # placeholder
    pass  # TODO: add support


class SimServoMotor:  # placeholder
    pass  # TODO: add support


class SimSensor(SimDevice, Sensor):
    DRIVER_NAMES = ['lego-sensor']

    def __init__(self, env_sim: EnvironmentSimulator, address=None, name_pattern=Sensor.SYSTEM_DEVICE_NAME_CONVENTION,
                 name_exact=False, **kwargs):
        Sensor.__init__(self, address, name_pattern, name_exact, **kwargs)
        if address is not None:
            kwargs['address'] = address
        SimDevice.__init__(self, env_sim, self.SYSTEM_CLASS_NAME,
                           name_pattern, name_exact, **kwargs)


def list_sim_sensors(sim_environment, name_pattern=Sensor.SYSTEM_DEVICE_NAME_CONVENTION, **kwargs):
    return (SimSensor(sim_environment, name_pattern=name, name_exact=True)
            for name in list_sim_device_names(Sensor.SYSTEM_CLASS_NAME, name_pattern, **kwargs))


class SimI2cSensor:  # placeholder
    pass  # TODO: add support


class SimTouchSensor(SimSensor, TouchSensor):
    DRIVER_NAMES = ['lego-ev3-touch', 'lego-nxt-touch']

    def __init__(self, env_sim: EnvironmentSimulator, address=None,
                 name_pattern=TouchSensor.SYSTEM_DEVICE_NAME_CONVENTION, name_exact=False, **kwargs):
        TouchSensor.__init__(self, address, name_pattern, name_exact, **kwargs)
        SimSensor.__init__(self, env_sim, address, name_pattern, name_exact,
                           driver_name=self.DRIVER_NAMES, **kwargs)


class SimColorSensor(SimSensor, ColorSensor):
    DRIVER_NAMES = ['lego-ev3-color']

    def __init__(self, env_sim: EnvironmentSimulator, address=None,
                 name_pattern=ColorSensor.SYSTEM_DEVICE_NAME_CONVENTION, name_exact=False, **kwargs):
        ColorSensor.__init__(self, address, name_pattern, name_exact, **kwargs)
        SimSensor.__init__(self, env_sim, address, name_pattern, name_exact,
                           driver_name=self.DRIVER_NAMES, **kwargs)


class SimUltrasonicSensor(SimSensor, UltrasonicSensor):
    DRIVER_NAMES = ['lego-ev3-us', 'lego-nxt-us']

    def __init__(self, env_sim: EnvironmentSimulator, address=None,
                 name_pattern=UltrasonicSensor.SYSTEM_DEVICE_NAME_CONVENTION, name_exact=False, **kwargs):
        UltrasonicSensor.__init__(self, address, name_pattern, name_exact, **kwargs)
        SimSensor.__init__(self, env_sim, address, name_pattern, name_exact,
                           driver_name=self.DRIVER_NAMES, **kwargs)


class SimGyroSensor(SimSensor, GyroSensor):
    DRIVER_NAMES = ['lego-ev3-gyro']

    def __init__(self, env_sim: EnvironmentSimulator, address=None,
                 name_pattern=GyroSensor.SYSTEM_DEVICE_NAME_CONVENTION, name_exact=False, **kwargs):
        GyroSensor.__init__(self, address, name_pattern, name_exact, **kwargs)
        SimSensor.__init__(self, env_sim, address, name_pattern, name_exact,
                           driver_name=self.DRIVER_NAMES, **kwargs)


class SimInfraredSensor(SimSensor, InfraredSensor):
    DRIVER_NAMES = ['lego-ev3-ir']

    def __init__(self, env_sim: EnvironmentSimulator, address=None,
                 name_pattern=InfraredSensor.SYSTEM_DEVICE_NAME_CONVENTION, name_exact=False, **kwargs):
        InfraredSensor.__init__(self, address, name_pattern, name_exact, **kwargs)
        SimSensor.__init__(self, env_sim, address, name_pattern, name_exact,
                           driver_name=self.DRIVER_NAMES, **kwargs)


class SimSoundSensor(SimSensor, SoundSensor):
    DRIVER_NAMES = ['lego-nxt-sound']

    def __init__(self, env_sim: EnvironmentSimulator, address=None,
                 name_pattern=SoundSensor.SYSTEM_DEVICE_NAME_CONVENTION, name_exact=False, **kwargs):
        SoundSensor.__init__(self, address, name_pattern, name_exact, **kwargs)
        SimSensor.__init__(self, env_sim, address, name_pattern, name_exact,
                           driver_name=self.DRIVER_NAMES, **kwargs)


class SimLightSensor(SimSensor, LightSensor):
    DRIVER_NAMES = ['lego-nxt-light']

    def __init__(self, env_sim: EnvironmentSimulator, address=None,
                 name_pattern=LightSensor.SYSTEM_DEVICE_NAME_CONVENTION, name_exact=False, **kwargs):
        LightSensor.__init__(self, address, name_pattern, name_exact, **kwargs)
        SimSensor.__init__(self, env_sim, address, name_pattern, name_exact,
                           driver_name=self.DRIVER_NAMES, **kwargs)


# class SimLed(SimDevice, Led):
#     def __init__(self, env_sim: EnvironmentSimulator, address=None,
#                  name_pattern=Led.SYSTEM_DEVICE_NAME_CONVENTION, name_exact=False, **kwargs):
#         Led.__init__(self, address, name_pattern, name_exact, **kwargs)
#         if address is not None:
#             kwargs['address'] = address
#         SimDevice.__init__(self, env_sim, address, name_pattern, name_exact, **kwargs)
#
#     @property
#     def trigger(self):
#         self._trigger, value = self.get_attr_from_set(self._trigger, 'trigger')
#         return value
#
#     @trigger.setter
#     def trigger(self, value):
#         self._trigger = self.set_attr_string(self._trigger, 'trigger', value)


class SimPowerSupply:  # placeholder
    pass  # TODO: add support


class SimLegoPort:  # placeholder
    pass  # TODO: add support


# class SimLeds(object):
#     def __init__(self, sim_environment):
#         self.red_left = SimLed(sim_environment, name_pattern='ev3:left:red:ev3dev')
#         self.red_right = SimLed(sim_environment, name_pattern='ev3:right:red:ev3dev')
#         self.green_left = SimLed(sim_environment, name_pattern='ev3:left:green:ev3dev')
#         self.green_right = SimLed(sim_environment, name_pattern='ev3:right:green:ev3dev')
#
#         self.LEFT = [self.red_left, self.green_left]
#         self.RIGHT = [self.red_right, self.green_right]
#
#         self.BLACK = [0, 0]
#         self.RED = [1, 0]
#         self.GREEN = [0, 1]
#         self.AMBER = [1, 1]
#         self.ORANGE = [1, 0.5]
#         self.YELLOW = [0.1, 1]
#
#     def set_color(self, group, color, pct=1):
#         for l, v in zip(group, color):
#             l.brightness_pct = v * pct
#
#     def set(self, group, **kwargs):
#         for led in group:
#             for k in kwargs:
#                 setattr(led, k, kwargs[k])
#
#     def all_off(self):
#         self.red_left.brightness = 0
#         self.red_right.brightness = 0
#         self.green_left.brightness = 0
#         self.green_right.brightness = 0


def _gen_hw_map() -> dict:
    hws = (
        (SimDevice, Device),

        (SimMotor, Motor),
        (SimLargeMotor, LargeMotor),
        (SimMediumMotor, MediumMotor),

        (SimSensor, Sensor),
        (SimTouchSensor, TouchSensor),
        (SimColorSensor, ColorSensor),
        (SimUltrasonicSensor, UltrasonicSensor),
        (SimGyroSensor, GyroSensor),
        (SimInfraredSensor, InfraredSensor),
        (SimSoundSensor, SoundSensor),
        (SimLightSensor, LightSensor),
        # LedDriver
    )

    hw_map = {}
    for hw_types in hws:
        for driver_name in hw_types[0].DRIVER_NAMES:
            hw_map[driver_name] = hw_types
    return hw_map


HW_MAP = _gen_hw_map()
