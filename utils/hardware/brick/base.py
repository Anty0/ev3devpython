from ev3dev.auto import Motor, Sensor

from utils.calc import dimensions as dp
from utils.graphics.drawer import Drawer
from utils.hardware.brick.active_bricks_info_provider import ActiveBricksInfoProvider
from utils.hardware.brick.position import BrickPosition, RelativeBrickPosition
from utils.hardware.propulsion import ScannerPropulsionInfo
from utils.hardware.simulation.world import World
from utils.hardware.wheel import WheelInfo


class Brick:
    def __init__(self, position: BrickPosition):
        self.position = position
        self.offset_center = None
        self.size = None
        self.color = None

        self.hw_parent_brick = None
        self.hw_class = 'unknown'
        self.hw_driver = None
        self.hw_id = 'unknown'

    def resolve_parent(self):
        brick = self
        while brick.hw_parent_brick is not None:
            brick = brick.hw_parent_brick
        return brick

    # def _position_in_world(self, robot_position: dp.Position,
    #                        active_bricks_info_provider: ActiveBricksInfoProvider or None):
    #     brick_position = self.position.get(active_bricks_info_provider).copy()
    #     brick_position.point.rotate(robot_position.angle).move(robot_position.point)
    #     brick_position.angle.rotate(robot_position.angle)
    #     return brick_position

    def _bounds_in_world(self, world: World, active_bricks_info_provider: ActiveBricksInfoProvider or None):
        brick_position = self.position.get(active_bricks_info_provider).copy()
        center_position = world.pos_on_pos(brick_position.point, brick_position.angle)

        width = self.size.width
        height = self.size.height

        ltp = dp.Point(-(width / 2), -(height / 2), 0)
        rbp = dp.Point(width / 2, height / 2, 0)

        if self.offset_center is not None:
            move = self.offset_center.copy().negate()
            ltp.move(move)
            rbp.move(move)

        ltp.rotate(center_position.angle).move(center_position.point)
        rbp.rotate(center_position.angle).move(center_position.point)

        return ltp.x, ltp.y, rbp.x, rbp.y

    def draw_2d(self, world: World, active_bricks_info_provider: ActiveBricksInfoProvider or None,
                canvas_drawer: Drawer):
        if self.size is None or self.color is None:
            return

        bounds = self._bounds_in_world(world, active_bricks_info_provider)
        # print(bounds)
        canvas_drawer.rectangle(*bounds, fill=self.color.to_str(include_alpha=False))


class ConnectableBrick(Brick):
    def __init__(self, position: BrickPosition):
        super().__init__(position)
        self.hw_class = 'unknown'
        self.hw_driver = 'unknown'
        self.hw_id = 'unknown'


class ActiveBrick(ConnectableBrick):
    def __init__(self, position: BrickPosition):
        super().__init__(position)


class MotorBrick(ActiveBrick):
    ALL_COMMANDS = [Motor.COMMAND_RUN_FOREVER, Motor.COMMAND_RUN_TO_ABS_POS, Motor.COMMAND_RUN_TO_REL_POS,
                    Motor.COMMAND_RUN_TIMED, Motor.COMMAND_RUN_DIRECT, Motor.COMMAND_STOP, Motor.COMMAND_RESET]

    def __init__(self, position: BrickPosition):
        super().__init__(position)
        self.hw_class = Motor.SYSTEM_CLASS_NAME
        self.hw_driver = 'lego-motor'
        self.hw_id = 'motor'
        self.hw_commands = []
        self.hw_count_per_rot = None
        self.hw_count_per_m = None  # TODO: support
        self.hw_full_travel_count = None  # TODO: support
        self.hw_max_speed = None
        self.hw_position_range = None


class SensorBrick(ConnectableBrick):
    def __init__(self, position: BrickPosition):
        super().__init__(position)
        self.hw_class = Sensor.SYSTEM_CLASS_NAME
        self.hw_driver = 'lego-sensor'
        self.hw_id = 'sensor'


class WheelBrick(Brick):
    def __init__(self, propulsion_brick: ActiveBrick, wheel_info: WheelInfo, position: BrickPosition = None):
        if position is None:
            propulsion_position_neg = propulsion_brick.position.get(None).copy().negate()
            position_offset = dp.Position(
                wheel_info.position.point.copy()
                    .move(propulsion_position_neg.point)
                    .rotate(propulsion_position_neg.angle),
                wheel_info.position.angle.copy().rotate(propulsion_position_neg.angle)
            )
            position = RelativeBrickPosition(position_offset, propulsion_brick,
                                             gear_rotation=position_offset.angle,
                                             gear_ratio=wheel_info.gear_ratio)
        super().__init__(position)
        self.propulsion_brick = propulsion_brick
        self.wheel_info = wheel_info

        self.size = wheel_info.size

        self.hw_parent_brick = propulsion_brick

    def draw_2d(self, world: World, active_bricks_info_provider: ActiveBricksInfoProvider or None,
                canvas_drawer: Drawer):
        if self.size is None:
            return

        brick_position = self.position.get(active_bricks_info_provider).copy()
        center_position = world.pos_on_pos(brick_position.point, brick_position.angle)

        width = self.size.width
        height = self.size.height

        ltp = dp.Point(-(width / 2), -(height / 2), 0)
        rbp = dp.Point(width / 2, height / 2, 0)

        if self.offset_center is not None:
            move = self.offset_center.copy().negate()
            ltp.move(move)
            rbp.move(move)

        ltp.rotate(center_position.angle).move(center_position.point)
        rbp.rotate(center_position.angle).move(center_position.point)

        chx = rbp.x - ltp.x
        chy = rbp.y - ltp.y

        move_x = (brick_position.angle.deg_y / 180) % 1
        inv_x = int((brick_position.angle.deg_y / 180) % 2)
        move_y = (brick_position.angle.deg_x / 180) % 1
        inv_y = int((brick_position.angle.deg_x / 180) % 2)

        fsx = chx / 4 * move_x
        x1 = ltp.x
        x2 = ltp.x + fsx
        x3 = ltp.x + fsx + (chx / 4) * 1
        x4 = ltp.x + fsx + (chx / 4) * 2
        x5 = ltp.x + fsx + (chx / 4) * 3
        x6 = rbp.x

        fsy = chy / 4 * move_y
        y1 = ltp.y
        y2 = ltp.y + fsy
        y3 = ltp.y + fsy + (chy / 4) * 1
        y4 = ltp.y + fsy + (chy / 4) * 2
        y5 = ltp.y + fsy + (chy / 4) * 3
        y6 = rbp.y

        # print(x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, x6, y6)

        canvas_drawer.rectangle(x1, y1, x2, y2, fill='black' if inv_x == inv_y else 'grey')
        canvas_drawer.rectangle(x2, y2, x3, y3, fill='grey' if inv_x == inv_y else 'black')
        canvas_drawer.rectangle(x3, y3, x4, y4, fill='black' if inv_x == inv_y else 'grey')
        canvas_drawer.rectangle(x4, y4, x5, y5, fill='grey' if inv_x == inv_y else 'black')
        canvas_drawer.rectangle(x5, y5, x6, y6, fill='black' if inv_x == inv_y else 'grey')


class ScannerBrick(Brick):
    def __init__(self, propulsion_info: ScannerPropulsionInfo, propulsion_brick: ActiveBrick,
                 scanner_head_mode_creator: callable, head_brick: SensorBrick):
        super().__init__(head_brick.position)
        self.propulsion_info = propulsion_info
        self.propulsion_brick = propulsion_brick

        self.scanner_head_mode_creator = scanner_head_mode_creator
        self.head_brick = head_brick

    def draw_2d(self, world: World, active_bricks_info_provider: ActiveBricksInfoProvider or None,
                canvas_drawer: Drawer):
        pass  # does nothing

# TODO: create

# class LedInterface(DeviceInterface):
#     def __init__(self, position: Position2D, name: str, *world_effects: WorldEffect):
#         DeviceInterface.__init__(self, position, *world_effects)
#         self.class_name = Led.SYSTEM_CLASS_NAME
#         self.driver_name = 'unknown'
#         self.name = name
#         self.max_brightness = None
#         self.brightness = 0
#         self.triggers = []
#         self.delay_on = None
#         self.delay_off = None
#
#
# class EV3LedInterface(LedInterface):
#     def __init__(self, position: Position2D, name: str, *world_effects: WorldEffect):
#         LedInterface.__init__(self, position, name, *world_effects)
#         self.driver_name = 'leds-pwm'
#         self.max_brightness = 255
#         self.brightness = 0
#         self.triggers = ['none', 'timer']
#         # none kbd-scrolllock kbd-numlock kbd-capslock kbd-kanalock kbd-shiftlock kbd-altgrlock kbd-ctrllock
#         # kbd-altlock kbd-shiftllock kbd-shiftrlock kbd-ctrlllock kbd-ctrlrlock mmc0 timer heartbeat default-on
#         # transient legoev3-battery-charging-or-full legoev3-battery-charging legoev3-battery-full
#         # legoev3-battery-charging-blink-full-solid rfkill0 rfkill1
#         self.delay_on = 500
#         self.delay_off = 500
#
#
# class PowerSupplyInterface(DeviceInterface):  # placeholder
#     pass  # TODO: add support
#
#
# class EV3LegoPortInterface(DeviceInterface):  # placeholder
#     pass  # TODO: add support
