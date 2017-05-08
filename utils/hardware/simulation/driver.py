import time

from ev3dev.auto import Motor, TouchSensor, ColorSensor, UltrasonicSensor, \
    GyroSensor, InfraredSensor, SoundSensor, LightSensor

from utils.hardware.brick.bricks import Bricks
from utils.hardware.simulation.brick_controller import BrickController, MotorBrickController, SensorBrickController, \
    TouchSensorBrickController, ColorSensorBrickController, UltrasonicSensorBrickController, GyroSensorBrickController, \
    InfraredSensorBrickController, SoundSensorBrickController, LightSensorBrickController


class DeviceDriver:
    DRIVER_NAME = 'unknown'

    def __init__(self, bricks: Bricks, brick_controller: BrickController):
        self.bricks = bricks
        self.brick_controller = brick_controller

    @property
    def brick(self):
        return self.brick_controller.brick

    @property
    def driver_name(self):
        return self.DRIVER_NAME


class MotorDriver(DeviceDriver):  # FIXME: return default value if brick have none value
    DRIVER_NAME = 'lego-motor'

    def __init__(self, bricks: Bricks, brick_controller: MotorBrickController):
        DeviceDriver.__init__(self, bricks, brick_controller)
        self._last_command = Motor.COMMAND_STOP
        self._last_command_args = {'stop_action': Motor.STOP_ACTION_COAST}

        self._command = Motor.COMMAND_STOP
        self._duty_cycle_sp = 0
        self._polarity = Motor.POLARITY_NORMAL
        self._position_sp = 0
        self._speed_sp = 0
        self._ramp_up_sp = 0  # TODO: extract from ev3dev drivers
        self._ramp_down_sp = 0  # TODO: extract from ev3dev drivers
        self._state = []
        self._stop_action = Motor.STOP_ACTION_COAST
        self._stop_actions = [Motor.STOP_ACTION_COAST, Motor.STOP_ACTION_BRAKE, Motor.STOP_ACTION_HOLD]
        self._time_sp = 0

    @property
    def address(self):
        return str(self.bricks.brick_port(self.brick))

    @property
    def command(self):
        raise Exception("command is a write-only property!")

    @command.setter
    def command(self, value):
        if value not in self.brick.hw_commands:
            raise Exception('Invalid command: ' + value)

        actual_command = self._command
        if self._last_command != actual_command:
            if actual_command == Motor.COMMAND_RUN_FOREVER:
                self._last_command_args = {'speed': self._speed_sp}
                self.brick_controller.power = self.brick_controller.power_for_speed(self._last_command_args['speed'])
                self._state = [Motor.STATE_RUNNING]
            elif actual_command == Motor.COMMAND_RUN_TO_ABS_POS:
                self._last_command_args = {
                    'speed': self._speed_sp,
                    'position': self._position_sp,
                    'stop_action': self._stop_action
                }
                self.brick_controller.power = 0
                self._state = [Motor.STATE_RUNNING]
                # TODO: implement
            elif actual_command == Motor.COMMAND_RUN_TO_REL_POS:
                self._last_command_args = {
                    'speed': self._speed_sp,
                    'position': self.brick_controller.position + self._position_sp,
                    'stop_action': self._stop_action
                }
                self.brick_controller.power = 0
                self._state = [Motor.STATE_RUNNING]
                # TODO: implement
            elif actual_command == Motor.COMMAND_RUN_TIMED:
                self._last_command_args = {
                    'speed': self._speed_sp,
                    'start_time': time.time(),
                    'time': self._time_sp / 1000,
                    'stop_action': self._stop_action
                }
                self.brick_controller.power = 0
                self._state = [Motor.STATE_RUNNING]
                # TODO: implement
            elif actual_command == Motor.COMMAND_RUN_DIRECT:
                self._last_command_args = {}
                self.brick_controller.power = self._duty_cycle_sp
                self._state = [Motor.STATE_RUNNING]
            elif actual_command == Motor.COMMAND_STOP:
                self.brick_controller.power = 0
                self._last_command_args = {'stop_action': self._stop_action}
                self._state = [] if self._stop_action != Motor.STOP_ACTION_HOLD else [Motor.STATE_HOLDING]
            elif actual_command == Motor.COMMAND_RESET:
                actual_command = Motor.COMMAND_STOP
                self._last_command_args = {}
                self._duty_cycle_sp = 0
                self._polarity = Motor.POLARITY_NORMAL
                self._position_sp = 0
                self._speed_sp = 0
                self._ramp_up_sp = 0  # TODO: extract from ev3dev drivers
                self._ramp_down_sp = 0  # TODO: extract from ev3dev drivers
                self._state = []
                self._stop_action = Motor.STOP_ACTION_COAST
            self._last_command = actual_command

    @property
    def commands(self):
        commands = self.brick.hw_commands
        commands_len = len(commands)
        if commands_len == 0:
            return ''
        value = commands[0]
        for i in range(1, commands_len):
            value += ' ' + commands[i]
        return value

    @property
    def count_per_rot(self):
        return str(self.brick.hw_count_per_rot)

    @property
    def count_per_m(self):
        return str(self.brick.hw_count_per_m)

    @property
    def duty_cycle(self):
        return str(self.brick_controller.power)

    @property
    def duty_cycle_sp(self):
        return str(self._duty_cycle_sp)

    @duty_cycle_sp.setter
    def duty_cycle_sp(self, value):
        self._duty_cycle_sp = int(value)
        if self._last_command == Motor.COMMAND_RUN_DIRECT:
            self.brick_controller.power = self._duty_cycle_sp

    @property
    def full_travel_count(self):
        return str(self.brick.hw_full_travel_count)

    @property
    def polarity(self):
        return self._polarity

    @polarity.setter
    def polarity(self, value):
        if value not in (Motor.POLARITY_NORMAL, Motor.POLARITY_INVERSED):
            raise Exception('Invalid polarity: ' + value)
        self._polarity = value

    @property
    def position(self):
        return str(self.brick_controller.position)

    @position.setter
    def position(self, value):
        self.brick_controller.position = int(value)

    @property
    def position_sp(self):
        return str(self._position_sp)

    @position_sp.setter
    def position_sp(self, value):
        self._position_sp = int(value)

    @property
    def max_speed(self):
        return str(self.brick.hw_max_speed)

    @property
    def speed(self):
        return str(int(self.brick_controller.speed))

    @property
    def speed_sp(self):
        return str(self._speed_sp)

    @speed_sp.setter
    def speed_sp(self, value):
        if abs(int(value)) > self.brick.hw_max_speed:
            raise Exception('Invalid speed: ' + value)
        self._speed_sp = int(value)

    @property
    def ramp_up_sp(self):
        return str(self._ramp_up_sp)

    @ramp_up_sp.setter
    def ramp_up_sp(self, value):
        self._ramp_up_sp = int(value)

    @property
    def ramp_down_sp(self):
        return str(self._ramp_down_sp)

    @ramp_down_sp.setter
    def ramp_down_sp(self, value):
        self._ramp_down_sp = int(value)

    @property
    def state(self):
        state = self._state.copy()
        state_len = len(state)
        if state_len == 0:
            return ''
        value = state[0]
        for i in range(1, state_len):
            value += ' ' + state[i]
        return value

    @property
    def stop_action(self):
        return self._stop_action

    @stop_action.setter
    def stop_action(self, value):
        if value not in self._stop_actions:
            raise Exception('Invalid stop action: ' + value)
        self._stop_action = value

    @property
    def stop_actions(self):
        stop_actions = self._stop_actions.copy()
        stop_actions_len = len(stop_actions)
        if stop_actions_len == 0:
            return ''
        value = stop_actions[0]
        for i in range(1, stop_actions_len):
            value += ' ' + stop_actions[i]
        return value

    @property
    def time_sp(self):
        return str(self._time_sp)

    @time_sp.setter
    def time_sp(self, value):
        self._time_sp = int(value)


class NXTLargeMotorDriver(MotorDriver):
    DRIVER_NAME = 'lego-nxt-motor'


class EV3LargeMotorDriver(MotorDriver):
    DRIVER_NAME = 'lego-ev3-l-motor'


class EV3MediumMotorDriver(MotorDriver):
    DRIVER_NAME = 'lego-ev3-m-motor'


class SensorDriver(DeviceDriver):
    DRIVER_NAME = 'lego-sensor'

    def __init__(self, bricks: Bricks, brick_controller: SensorBrickController):
        DeviceDriver.__init__(self, bricks, brick_controller)
        self._decimals = {}
        self._num_values = {}
        self._units = {}

    @property
    def address(self):
        return str(self.bricks.brick_port(self.brick))

    @property
    def command(self):
        raise Exception("command is a write-only property!")

    @command.setter
    def command(self, value):
        commands = self.brick_controller.COMMANDS
        if commands is None or value not in commands:
            raise Exception('Invalid command: ' + value)
        self.brick_controller.exec_command(value)

    @property
    def commands(self):
        commands = self.brick_controller.COMMANDS
        if commands is None:
            raise Exception('This sensor does not supports commands.')

        commands_len = len(commands)
        if commands_len == 0:
            return ''
        value = commands[0]
        for i in range(1, commands_len):
            value += ' ' + commands[i]
        return value

    @property
    def decimals(self):
        return str(self._decimals[self.brick_controller.mode])

    @property
    def mode(self):
        return self.brick_controller.mode

    @mode.setter
    def mode(self, value):
        actual_mode = self.brick_controller.mode
        if actual_mode == value:
            return
        if value not in self.brick_controller.MODES:
            raise Exception('Invalid mode: ' + value)
        self._on_mode_change(actual_mode, value)
        self.brick_controller.mode = value

    def _on_mode_change(self, old_mode, new_mode):
        pass

    @property
    def modes(self):
        modes = self.brick_controller.MODES
        modes_len = len(modes)
        if modes_len == 0:
            return ''
        value = modes[0]
        for i in range(1, modes_len):
            value += ' ' + modes[i]
        return value

    @property
    def num_values(self):
        return str(self._num_values[self.brick_controller.mode])

    @property
    def units(self):
        return str(self._units[self.brick_controller.mode])  # TODO: better simulation of none units

    @property
    def bin_data_format(self):
        raise Exception('Unsupported by simulator')

    @property
    def bin_data(self):
        raise Exception('Unsupported by simulator')

    @property
    def value0(self):
        return self.brick_controller.value(0)

    @property
    def value1(self):
        return self.brick_controller.value(1)

    @property
    def value2(self):
        return self.brick_controller.value(2)

    @property
    def value3(self):
        return self.brick_controller.value(3)

    @property
    def value4(self):
        return self.brick_controller.value(4)

    @property
    def value5(self):
        return self.brick_controller.value(5)

    @property
    def value6(self):
        return self.brick_controller.value(6)

    @property
    def value7(self):
        return self.brick_controller.value(7)


class TouchSensorDriver(SensorDriver):
    DRIVER_NAME = 'lego-touch'

    def __init__(self, bricks: Bricks, brick_controller: TouchSensorBrickController):
        DeviceDriver.__init__(self, bricks, brick_controller)
        self._decimals = {TouchSensor.MODE_TOUCH: 0}
        self._num_values = {TouchSensor.MODE_TOUCH: 1}
        self._units = {TouchSensor.MODE_TOUCH: None}


class EV3TouchSensorDriver(TouchSensorDriver):
    DRIVER_NAME = 'lego-ev3-touch'


class NXTTouchSensorDriver(TouchSensorDriver):
    DRIVER_NAME = 'lego-nxt-touch'


class ColorSensorDriver(SensorDriver):
    DRIVER_NAME = 'lego-ev3-color'

    def __init__(self, bricks: Bricks, brick_controller: ColorSensorBrickController):
        DeviceDriver.__init__(self, bricks, brick_controller)
        self._decimals = {
            ColorSensor.MODE_COL_REFLECT: 0,
            ColorSensor.MODE_COL_AMBIENT: 0,
            ColorSensor.MODE_COL_COLOR: 0,
            ColorSensor.MODE_REF_RAW: 0,
            ColorSensor.MODE_RGB_RAW: 0
        }
        self._num_values = {
            ColorSensor.MODE_COL_REFLECT: 1,
            ColorSensor.MODE_COL_AMBIENT: 1,
            ColorSensor.MODE_COL_COLOR: 1,
            ColorSensor.MODE_REF_RAW: 2,
            ColorSensor.MODE_RGB_RAW: 3
        }
        self._units = {
            ColorSensor.MODE_COL_REFLECT: 'pct',
            ColorSensor.MODE_COL_AMBIENT: 'pct',
            ColorSensor.MODE_COL_COLOR: 'pct',
            ColorSensor.MODE_REF_RAW: None,
            ColorSensor.MODE_RGB_RAW: None
        }


class UltrasonicSensorDriver(SensorDriver):
    DRIVER_NAME = 'lego-us'

    def __init__(self, bricks: Bricks, brick_controller: UltrasonicSensorBrickController):
        DeviceDriver.__init__(self, bricks, brick_controller)
        ev3 = self.DRIVER_NAME == 'lego-ev3-us'
        self._decimals = {
            UltrasonicSensor.MODE_US_DIST_CM: 1 if ev3 else 0,
            UltrasonicSensor.MODE_US_DIST_IN: 1,
            UltrasonicSensor.MODE_US_LISTEN: 0,
            UltrasonicSensor.MODE_US_SI_CM: 1 if ev3 else 0,
            UltrasonicSensor.MODE_US_SI_IN: 1
        }
        self._num_values = {
            UltrasonicSensor.MODE_US_DIST_CM: 1,
            UltrasonicSensor.MODE_US_DIST_IN: 1,
            UltrasonicSensor.MODE_US_LISTEN: 1,
            UltrasonicSensor.MODE_US_SI_CM: 1,
            UltrasonicSensor.MODE_US_SI_IN: 1
        }
        self._units = {
            UltrasonicSensor.MODE_US_DIST_CM: 'cm',
            UltrasonicSensor.MODE_US_DIST_IN: 'in',
            UltrasonicSensor.MODE_US_LISTEN: None,
            UltrasonicSensor.MODE_US_SI_CM: 'cm',
            UltrasonicSensor.MODE_US_SI_IN: 'in'
        }


class EV3UltrasonicSensorDriver(UltrasonicSensorDriver):
    DRIVER_NAME = 'lego-ev3-us'


class NXTUltrasonicSensorDriver(UltrasonicSensorDriver):
    DRIVER_NAME = 'lego-nxt-us'


class GyroSensorDriver(SensorDriver):
    DRIVER_NAME = 'lego-ev3-gyro'

    def __init__(self, bricks: Bricks, brick_controller: GyroSensorBrickController):
        DeviceDriver.__init__(self, bricks, brick_controller)
        self._decimals = {
            GyroSensor.MODE_GYRO_ANG: 0,
            GyroSensor.MODE_GYRO_RATE: 0,
            GyroSensor.MODE_GYRO_FAS: 0,
            GyroSensor.MODE_GYRO_G_A: 0,
            GyroSensor.MODE_GYRO_CAL: 0
        }
        self._num_values = {
            GyroSensor.MODE_GYRO_ANG: 1,
            GyroSensor.MODE_GYRO_RATE: 1,
            GyroSensor.MODE_GYRO_FAS: 1,
            GyroSensor.MODE_GYRO_G_A: 2,
            GyroSensor.MODE_GYRO_CAL: 4
        }
        self._units = {
            GyroSensor.MODE_GYRO_ANG: 'deg',
            GyroSensor.MODE_GYRO_RATE: 'd/s',
            GyroSensor.MODE_GYRO_FAS: None,
            GyroSensor.MODE_GYRO_G_A: None,
            GyroSensor.MODE_GYRO_CAL: None
        }


class InfraredSensorDriver(SensorDriver):
    DRIVER_NAME = 'lego-ev3-ir'

    def __init__(self, bricks: Bricks, brick_controller: InfraredSensorBrickController):
        DeviceDriver.__init__(self, bricks, brick_controller)
        self._decimals = {
            InfraredSensor.MODE_IR_PROX: 0,
            InfraredSensor.MODE_IR_SEEK: 0,
            InfraredSensor.MODE_IR_REMOTE: 0,
            InfraredSensor.MODE_IR_REM_A: 0,
            InfraredSensor.MODE_IR_CAL: 0
        }
        self._num_values = {
            InfraredSensor.MODE_IR_PROX: 1,
            InfraredSensor.MODE_IR_SEEK: 8,
            InfraredSensor.MODE_IR_REMOTE: 4,
            InfraredSensor.MODE_IR_REM_A: 1,
            InfraredSensor.MODE_IR_CAL: 2
        }
        self._units = {
            InfraredSensor.MODE_IR_PROX: 'pct',
            InfraredSensor.MODE_IR_SEEK: 'pct',
            InfraredSensor.MODE_IR_REMOTE: 'btn',
            InfraredSensor.MODE_IR_REM_A: None,
            InfraredSensor.MODE_IR_CAL: None
        }


class SoundSensorDriver(SensorDriver):
    DRIVER_NAME = 'lego-nxt-sound'

    def __init__(self, bricks: Bricks, brick_controller: SoundSensorBrickController):
        DeviceDriver.__init__(self, bricks, brick_controller)
        self._decimals = {
            SoundSensor.MODE_DB: 1,
            SoundSensor.MODE_DBA: 1
        }
        self._num_values = {
            SoundSensor.MODE_DB: 1,
            SoundSensor.MODE_DBA: 1
        }
        self._units = {
            SoundSensor.MODE_DB: 'pct',
            SoundSensor.MODE_DBA: 'pct'
        }


class LightSensorDriver(SensorDriver):
    DRIVER_NAME = 'lego-nxt-light'

    def __init__(self, bricks: Bricks, brick_controller: LightSensorBrickController):
        DeviceDriver.__init__(self, bricks, brick_controller)
        self._decimals = {
            LightSensor.MODE_REFLECT: 1,
            LightSensor.MODE_AMBIENT: 1
        }
        self._num_values = {
            LightSensor.MODE_REFLECT: 1,
            LightSensor.MODE_AMBIENT: 1
        }
        self._units = {
            LightSensor.MODE_REFLECT: 'pct',
            LightSensor.MODE_AMBIENT: 'pct'
        }

        # class LedDriver(DeviceDriver):
        #     DRIVER_NAME = 'leds-pwm'
        #
        # def __init__(self, world: World, device_interface: LedInterface):
        #     DeviceDriver.__init__(self, world, device_interface)
        #     self._max_brightness = device_interface.max_brightness
        #     self._brightness = device_interface.brightness
        #     self._triggers = device_interface.triggers
        #     self._trigger = 'none'
        #     self._delay_on = device_interface.delay_on
        #     self._delay_off = device_interface.delay_off
        #
        # @property
        # def max_brightness(self):
        #     return str(self._max_brightness)
        #
        # @property
        # def brightness(self):
        #     return str(self._brightness)
        #
        # @brightness.setter
        # def brightness(self, value):
        #     self._brightness = int(value)
        #
        # @property
        # def trigger(self):
        #     triggers_len = len(self._triggers)
        #     if triggers_len == 0:
        #         return ''
        #     value = self._triggers[0]
        #     for i in range(1, triggers_len):
        #         value += ' ' + self._triggers[i]
        #     return value
        #
        # @trigger.setter
        # def trigger(self, value):
        #     if value not in self._triggers:
        #         raise Exception()
        #     self._trigger = value
        #     # TODO: apply trigger
        #
        # @property
        # def delay_on(self):
        #     return str(self._delay_on)
        #
        # @delay_on.setter
        # def delay_on(self, value):
        #     self._delay_on = int(value)
        #
        # @property
        # def delay_off(self):
        #     return str(self._delay_off)
        #
        # @delay_off.setter
        # def delay_off(self, value):
        #     self._delay_off = int(value)
        # pass  # TODO: implement


def _gen_drivers_map():
    drivers = (
        DeviceDriver,

        MotorDriver,
        NXTLargeMotorDriver,
        EV3LargeMotorDriver,
        EV3MediumMotorDriver,

        SensorDriver,
        TouchSensorDriver,
        EV3TouchSensorDriver,
        NXTTouchSensorDriver,
        ColorSensorDriver,
        UltrasonicSensorDriver,
        EV3UltrasonicSensorDriver,
        NXTUltrasonicSensorDriver,
        GyroSensorDriver,
        InfraredSensorDriver,
        SoundSensorDriver,
        LightSensorDriver,
        # LedDriver
    )

    drivers_map = {}
    for driver_type in drivers:
        drivers_map[driver_type.DRIVER_NAME] = driver_type
    return drivers_map


DRIVERS_MAP = _gen_drivers_map()
