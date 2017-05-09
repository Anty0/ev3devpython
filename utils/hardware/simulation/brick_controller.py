import math
import time

from ev3dev.auto import TouchSensor, ColorSensor, UltrasonicSensor, \
    GyroSensor, InfraredSensor, SoundSensor, LightSensor

from utils.calc import dimensions as dp
from utils.hardware.brick.active_bricks_info_provider import ActiveBricksInfoProvider, PositionChange
from utils.hardware.brick.base import Brick, ConnectableBrick, ActiveBrick, MotorBrick, SensorBrick
from utils.hardware.brick.bricks import Bricks
from utils.hardware.brick.sensors import TouchSensorBrick, ColorSensorBrick, UltrasonicSensorBrick, GyroSensorBrick, \
    InfraredSensorBrick, SoundSensorBrick, LightSensorBrick
from utils.hardware.simulation.world import World
from utils.utils import crop_m


class BrickController:
    def __init__(self, bricks_info_provider: ActiveBricksInfoProvider, world: World, brick: Brick):
        self._bricks_info_provider = bricks_info_provider
        self.world = world
        self.brick = brick

    @property
    def _brick_position(self) -> dp.Position:
        return self.brick.position.get(self._bricks_info_provider)


class ActiveBrickController(BrickController):
    def active_position_change(self) -> PositionChange or None:
        return None


class MotorBrickController(ActiveBrickController):
    def __init__(self, bricks_info_provider: ActiveBricksInfoProvider, world: World, brick: MotorBrick):
        super().__init__(bricks_info_provider, world, brick)
        self._position_change = PositionChange(dp.Angle(), dp.Point(0, 0, 0))
        self._power = 0
        self._position = 0
        self._last_update = time.time()

    def active_position_change(self):
        self._calc_pos()
        return self._position_change

    @property
    def power(self) -> int:
        return self._power

    @power.setter
    def power(self, power: int):
        if power > 100 or power < -100:
            raise Exception('Power out of range.')
        self._calc_pos()
        self._power = int(power)

    @property
    def position(self) -> int:
        self._calc_pos()
        return int(self._position)

    @position.setter
    def position(self, position: int):
        self._calc_pos()
        self._position = int(position)
        self._calc_pos()

    @staticmethod
    def power_for_speed(speed: float):
        return (2 * speed) / (speed + 1)

    @property
    def speed(self) -> float:
        power = self._power
        if abs(power) < 10:
            return 0

        max_speed = self.brick.hw_max_speed if self.brick.hw_max_speed is not None else 1050

        mul = 1 if power > 0 else -1
        power = (power - (10 * mul)) / 90
        speed = power / (abs(1 - power) + 1)
        speed *= max_speed * 1.2
        return speed

    def _calc_pos(self):
        current_time = time.time()
        time_change = current_time - self._last_update
        self._last_update = current_time

        position = self._position + (self.speed * time_change)
        if self.brick.hw_position_range is not None:
            position = self.brick.hw_position_range.crop(position)

        self._position = position
        self._position_change.rotation.rad_y = 0 if self.brick.hw_count_per_rot is None else \
            self._position / self.brick.hw_count_per_rot * (2 * math.pi)
        # TODO: support for moving motors


class SensorBrickController(BrickController):
    COMMANDS = None
    MODES = []
    DEFAULT_MODE = None

    def __init__(self, bricks_info_provider: ActiveBricksInfoProvider, world: World, brick: SensorBrick):
        super().__init__(bricks_info_provider, world, brick)
        self._mode = self.DEFAULT_MODE

    def exec_command(self, command):
        pass

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode):
        if self._mode == mode:
            return

        if mode not in self.MODES:
            raise Exception('Unknown mode: ' + mode)

        self._on_mode_change(self._mode, mode)
        self._mode = mode

    def _on_mode_change(self, old_mode, new_mode):
        pass

    def value(self, n=0):
        pass


class TouchSensorBrickController(SensorBrickController):
    MODES = [TouchSensor.MODE_TOUCH]
    DEFAULT_MODE = TouchSensor.MODE_TOUCH

    def value(self, n=0):
        position = self._brick_position
        if n == 0:
            if self._mode == TouchSensor.MODE_TOUCH:
                return int(self.world.pos_in_wall(position.point, position.angle))
        raise Exception('Unknown value: ' + str(n))


class ColorSensorBrickController(SensorBrickController):
    MODES = [ColorSensor.MODE_COL_REFLECT, ColorSensor.MODE_COL_AMBIENT, ColorSensor.MODE_COL_COLOR,
             ColorSensor.MODE_REF_RAW, ColorSensor.MODE_RGB_RAW]
    DEFAULT_MODE = ColorSensor.MODE_COL_REFLECT

    def value(self, n=0):
        position = self._brick_position
        if n == 0:
            if self._mode == ColorSensor.MODE_COL_REFLECT:
                return int(self.world.reflect_on_pos(position.point, position.angle))
            if self._mode == ColorSensor.MODE_COL_AMBIENT:
                return int(self.world.light_on_pos(position.point, position.angle))
            if self._mode == ColorSensor.MODE_COL_COLOR:
                return int(0)  # TODO: implement
            if self._mode == ColorSensor.MODE_REF_RAW:
                return int(0)  # TODO: implement
            if self._mode == ColorSensor.MODE_RGB_RAW:
                return int(self.world.color_rgb_on_pos(position.point, position.angle)[0])
        elif n == 1:
            if self._mode == ColorSensor.MODE_REF_RAW:
                return int(0)  # TODO: implement
            if self._mode == ColorSensor.MODE_RGB_RAW:
                return int(self.world.color_rgb_on_pos(position.point, position.angle)[1])
        elif n == 2:
            if self._mode == ColorSensor.MODE_RGB_RAW:
                return int(self.world.color_rgb_on_pos(position.point, position.angle)[2])
        raise Exception('Unknown value: ' + str(n))


class UltrasonicSensorBrickController(SensorBrickController):
    MODES = [UltrasonicSensor.MODE_US_DIST_CM, UltrasonicSensor.MODE_US_DIST_IN, UltrasonicSensor.MODE_US_LISTEN,
             UltrasonicSensor.MODE_US_SI_CM, UltrasonicSensor.MODE_US_SI_IN]
    DEFAULT_MODE = UltrasonicSensor.MODE_US_DIST_CM

    def __init__(self, bricks_info_provider: ActiveBricksInfoProvider, world: World, brick: SensorBrick):
        super().__init__(bricks_info_provider, world, brick)
        self._tmp_value = 0
        self._on_mode_change(None, self._mode)

    def _on_mode_change(self, old_mode, new_mode):
        if new_mode == UltrasonicSensor.MODE_US_SI_CM or new_mode == UltrasonicSensor.MODE_US_SI_IN:
            position = self._brick_position
            self._tmp_value = self.world.distance_from_wall_on_pos(position.point, position.angle)
        else:
            self._tmp_value = 0

    def value(self, n=0):
        if n == 0:
            position = self._brick_position
            is_ev3 = self.brick.hw_driver == 'lego-ev3-us'
            if self._mode == UltrasonicSensor.MODE_US_DIST_CM:
                distance = crop_m(self.world.distance_from_wall_on_pos(position.point, position.angle), 0, 255)
                if is_ev3:
                    distance *= 10
                return int(distance)  # map must be in cm
            if self._mode == UltrasonicSensor.MODE_US_DIST_IN:
                distance = crop_m(self.world.distance_from_wall_on_pos(position.point, position.angle) * 10, 0, 1003)
                return int(distance)  # map must be in inch
            if self._mode == UltrasonicSensor.MODE_US_LISTEN:
                return int(0)  # TODO: add support
            if self._mode == UltrasonicSensor.MODE_US_SI_CM:
                distance = crop_m(self._tmp_value, 0, 255)
                if is_ev3:
                    distance *= 10
                return int(distance)  # map must be in cm
            if self._mode == UltrasonicSensor.MODE_US_SI_IN:
                distance = crop_m(self._tmp_value * 10, 0, 1003)
                return int(distance)  # map must be in inch
        raise Exception('Unknown value: ' + str(n))


class GyroSensorBrickController(SensorBrickController):
    MODES = [GyroSensor.MODE_GYRO_ANG, GyroSensor.MODE_GYRO_RATE, GyroSensor.MODE_GYRO_FAS,
             GyroSensor.MODE_GYRO_G_A, GyroSensor.MODE_GYRO_CAL]
    DEFAULT_MODE = GyroSensor.MODE_GYRO_ANG

    def __init__(self, bricks_info_provider: ActiveBricksInfoProvider, world: World, brick: SensorBrick):
        super().__init__(bricks_info_provider, world, brick)
        self._start_angle = None
        self._on_mode_change(None, self._mode)

    def _on_mode_change(self, old_mode, new_mode):
        position = self._brick_position
        self._start_angle = self.world.pos_on_pos(position.point, position.angle).angle

    def value(self, n=0):
        if n == 0:
            if self._mode == GyroSensor.MODE_GYRO_ANG or self._mode == GyroSensor.MODE_GYRO_G_A:
                position = self._brick_position
                angle = self.world.pos_on_pos(position.point, position.angle).angle
                return angle.rad_z - self._start_angle.rad_z  # TODO: take care of sensor position angle
            if self._mode == GyroSensor.MODE_GYRO_RATE:
                return 0  # TODO: add support
            if self._mode == GyroSensor.MODE_GYRO_FAS:
                return 0  # TODO: add support
            if self._mode == GyroSensor.MODE_GYRO_CAL:
                return 0  # TODO: add support
        elif n == 1:
            if self._mode == GyroSensor.MODE_GYRO_G_A:
                return 0  # TODO: add support
            if self._mode == GyroSensor.MODE_GYRO_CAL:
                return 0  # TODO: add support
        elif n == 2:
            if self._mode == GyroSensor.MODE_GYRO_CAL:
                return 0  # TODO: add support
        elif n == 3:
            if self._mode == GyroSensor.MODE_GYRO_CAL:
                return 0  # TODO: add support
        raise Exception('Unknown value: ' + str(n))


class InfraredSensorBrickController(SensorBrickController):
    MODES = [InfraredSensor.MODE_IR_PROX, InfraredSensor.MODE_IR_SEEK, InfraredSensor.MODE_IR_REMOTE,
             InfraredSensor.MODE_IR_REM_A, InfraredSensor.MODE_IR_CAL]
    DEFAULT_MODE = InfraredSensor.MODE_IR_PROX

    def value(self, n=0):
        if n == 0:
            if self._mode == InfraredSensor.MODE_IR_PROX:
                position = self._brick_position
                distance = crop_m(self.world.distance_from_wall_on_pos(position.point, position.angle), 0, 70)
                return int(distance / 70 * 100)
            if self._mode == InfraredSensor.MODE_IR_SEEK:
                return 0  # TODO: add support
            if self._mode == InfraredSensor.MODE_IR_REMOTE:
                return 0  # TODO: add support
            if self._mode == InfraredSensor.MODE_IR_REM_A:
                return 0  # TODO: add support
            if self._mode == InfraredSensor.MODE_IR_CAL:
                return 0  # TODO: add support
        elif n == 1:
            if self._mode == InfraredSensor.MODE_IR_SEEK:
                return -128  # TODO: add support
            if self._mode == InfraredSensor.MODE_IR_REMOTE:
                return 0  # TODO: add support
            if self._mode == InfraredSensor.MODE_IR_CAL:
                return 0  # TODO: add support
        elif n == 2:
            if self._mode == InfraredSensor.MODE_IR_SEEK:
                return 0  # TODO: add support
            if self._mode == InfraredSensor.MODE_IR_REMOTE:
                return 0  # TODO: add support
        elif n == 3:
            if self._mode == InfraredSensor.MODE_IR_SEEK:
                return -128  # TODO: add support
            if self._mode == InfraredSensor.MODE_IR_REMOTE:
                return 0  # TODO: add support
        elif n == 4:
            if self._mode == InfraredSensor.MODE_IR_SEEK:
                return 0  # TODO: add support
        elif n == 5:
            if self._mode == InfraredSensor.MODE_IR_SEEK:
                return -128  # TODO: add support
        elif n == 6:
            if self._mode == InfraredSensor.MODE_IR_SEEK:
                return 0  # TODO: add support
        elif n == 7:
            if self._mode == InfraredSensor.MODE_IR_SEEK:
                return -128  # TODO: add support
        raise Exception('Unknown value: ' + str(n))


class SoundSensorBrickController(SensorBrickController):
    MODES = [SoundSensor.MODE_DB, SoundSensor.MODE_DBA]
    DEFAULT_MODE = SoundSensor.MODE_DB

    def value(self, n=0):
        if n == 0:
            if self._mode == SoundSensor.MODE_DB:
                return 0  # TODO: add support
            if self._mode == SoundSensor.MODE_DBA:
                return 0  # TODO: add support
        raise Exception('Unknown value: ' + str(n))


class LightSensorBrickController(SensorBrickController):
    MODES = [LightSensor.MODE_REFLECT, LightSensor.MODE_AMBIENT]
    DEFAULT_MODE = LightSensor.MODE_REFLECT

    def value(self, n=0):
        position = self._brick_position
        if n == 0:
            if self._mode == LightSensor.MODE_REFLECT:
                return int(self.world.reflect_on_pos(position.point, position.angle) * 10)
            if self._mode == LightSensor.MODE_AMBIENT:
                return int(self.world.light_on_pos(position.point, position.angle) * 10)
        raise Exception('Unknown value: ' + str(n))


CONTROLLERS_HIERARCHY_TREE = {
    Brick: (None, {
        ConnectableBrick: (BrickController, {
            ActiveBrick: (ActiveBrickController, {
                MotorBrick: (MotorBrickController, {})
            }),
            SensorBrick: (SensorBrickController, {
                TouchSensorBrick: (TouchSensorBrickController, {}),
                ColorSensorBrick: (ColorSensorBrickController, {}),
                UltrasonicSensorBrick: (UltrasonicSensorBrickController, {}),
                GyroSensorBrick: (GyroSensorBrickController, {}),
                InfraredSensorBrick: (InfraredSensorBrickController, {}),
                SoundSensorBrick: (SoundSensorBrickController, {}),
                LightSensorBrick: (LightSensorBrickController, {})
            })
        })
    })
}


class BricksControllers(ActiveBricksInfoProvider):
    def __init__(self, world: World, bricks: Bricks):
        self.world = world
        self.bricks = bricks

        self._controllers = {}

    @staticmethod
    def _controller_type(brick: Brick) -> type or None:
        controller_type = None
        hierarchy = CONTROLLERS_HIERARCHY_TREE
        found = True
        while found:
            found = False
            for brick_type in hierarchy.keys():
                if isinstance(brick, brick_type):
                    controller_type, hierarchy = hierarchy[brick_type]
                    found = True
                    break
        return controller_type

    def brick_controller(self, brick: Brick, resolve_parent: bool = True) -> BrickController or None:
        if resolve_parent:
            brick = brick.resolve_parent()

        if brick not in self._controllers:
            controller_type = self._controller_type(brick)
            self._controllers[brick] = controller_type(self, self.world, brick) \
                if controller_type is not None else None
        return self._controllers[brick]

    def position_change(self, brick: Brick, resolve_parent: bool = True) -> PositionChange or None:
        if resolve_parent:
            brick = brick.resolve_parent()

        if brick not in self._controllers:
            return None
        controller = self._controllers[brick]
        if not isinstance(controller, ActiveBrickController):
            return None
        return controller.active_position_change()
