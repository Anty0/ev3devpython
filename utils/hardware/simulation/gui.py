import itertools
import time
from threading import Thread

from tkinter import *

from utils.calc.color import argb_to_str
from utils.control.odometry import PositionsCollector
from utils.graphics.drawer import ScaledCanvasDrawer
from utils.hardware.brick.base import WheelBrick, ScannerBrick
from utils.hardware.generator import HWControllerGenerator
from utils.hardware.simulation.brick_controller import MotorBrickController


class WorldGui(Tk):
    SCALE_X = 1.5
    SCALE_Y = 1.5

    TAG_MAP = 'map'
    TAG_BRICKS = 'bricks'
    TAG_ROBOT_ROUTE = 'robot_route'
    TAG_BRICKS_INFO = 'bricks_info'

    def __init__(self, hw_generator: HWControllerGenerator):
        super().__init__()
        self.hw_generator = hw_generator
        world_map = self.hw_generator.environment_simulator.bricks_controllers.world.map

        self.wm_title("World")
        self.configure(background='white')

        self.canvas = Canvas(self, width=int(world_map.width * self.SCALE_X),
                             height=int(world_map.height * self.SCALE_Y), bg="white")
        self.canvas.pack()
        self.robot_canvas_drawer = ScaledCanvasDrawer(self.canvas, tag=self.TAG_BRICKS,
                                                      scale_x=self.SCALE_X, scale_y=self.SCALE_Y)

        self.bricks_drawer_thread = Thread(target=self._bricks_drawer_thread_loop,
                                           name='WorldGuiBricksDrawerThread', daemon=True)

        self.bricks_info_drawer_thread = Thread(target=self._bricks_info_drawer_thread_loop,
                                                name='WorldGuiBricksInfoDrawerThread', daemon=True)
        self.robot_positions_collector = PositionsCollector(
            self.hw_generator.environment_simulator.robot_position_updater.odometry)
        self.robot_positions_collector.cycle()

        self._draw_map()
        self._draw_bricks()
        self._draw_bricks_info()

    def mainloop(self, n=0):
        self.bricks_drawer_thread.start()
        self.bricks_info_drawer_thread.start()
        super().mainloop(n=n)

    def _bricks_drawer_thread_loop(self):
        while True:
            self._draw_bricks()
            time.sleep(0.2)

    def _bricks_info_drawer_thread_loop(self):
        while True:
            self._draw_bricks_info()
            time.sleep(0.2)

    def _draw_map(self):
        world_map = self.hw_generator.environment_simulator.bricks_controllers.world.map
        scale_x = self.SCALE_X
        scale_y = self.SCALE_Y

        self.world_map_image = PhotoImage(width=int(world_map.width * scale_x), height=int(world_map.height * scale_y))
        world_map_image = self.world_map_image
        for change in world_map.changes:
            x, y = change[0]
            if world_map.wall(x, y):
                color_str = argb_to_str(0, 0, 0)
            else:
                color_rgb = world_map.color_rgb(x, y)
                color_str = argb_to_str(color_rgb[0], color_rgb[1], color_rgb[2])
            # for ax, ay in ((0, 0), (0, 1), (1, 0), (1, 1)):  # supports only scale 2
            #     world_map_image.put(color_str, (int(x * scale_x) + ax, int(y * scale_y + ay)))
            world_map_image.put(color_str, (int(x * scale_x), int(y * scale_y)))
        self.canvas.delete(self.TAG_MAP)
        self.canvas.create_image(0, 0, image=world_map_image, anchor=NW, tags=self.TAG_MAP)

    def _draw_bricks(self):
        bricks_controllers = self.hw_generator.environment_simulator.bricks_controllers
        world = bricks_controllers.world
        self.robot_canvas_drawer.clear()
        for brick in bricks_controllers.bricks.tuple_bricks:
            brick.draw_2d(world, bricks_controllers, self.robot_canvas_drawer)

        scale_x = self.SCALE_X
        scale_y = self.SCALE_Y
        positions_collector = self.robot_positions_collector
        positions_collector.cycle()
        pos1 = positions_collector.positions[-2]
        pos2 = positions_collector.positions[-1]
        self.canvas.create_line(pos1[0] * scale_x, pos1[1] * scale_y,
                                pos2[0] * scale_x, pos2[1] * scale_y,
                                fill='black', tags=self.TAG_ROBOT_ROUTE)

    def _draw_bricks_info(self):
        bricks_controllers = self.hw_generator.environment_simulator.bricks_controllers
        world = bricks_controllers.world
        bricks = bricks_controllers.bricks

        texts = ['Robot:']
        robot_pos = world.pos_on_pos()
        texts.append('Position: ' + str(robot_pos))
        texts.append('Wheels:')
        for wheel_brick in bricks.bricks_of_type(WheelBrick):
            propulsion_brick = wheel_brick.resolve_parent()
            propulsion_port = bricks.brick_port(propulsion_brick)
            propulsion_brick_controller = bricks_controllers.brick_controller(propulsion_brick, resolve_parent=False)
            if isinstance(propulsion_brick_controller, MotorBrickController):
                position_info = str(propulsion_brick_controller.position) + ', ' + \
                                str(propulsion_brick_controller.active_position_change())
            else:
                position_change = propulsion_brick_controller.active_position_change()
                if position_change is None:
                    position_info = 'Unknown position'
                else:
                    position_info = str(position_change)

            texts.append('  Propulsion: ' + propulsion_port + ': ' + position_info)
            texts.append('  Wheel: ' + str(wheel_brick.position.get(bricks_controllers)))

        texts.append('Scanners:')
        for scanner_brick in bricks.bricks_of_type(ScannerBrick):
            propulsion_brick = scanner_brick.propulsion_brick.resolve_parent()
            propulsion_port = bricks.brick_port(propulsion_brick)
            propulsion_brick_controller = bricks_controllers.brick_controller(propulsion_brick, resolve_parent=False)
            if isinstance(propulsion_brick_controller, MotorBrickController):
                position_info = str(propulsion_brick_controller.position)
            else:
                position_change = propulsion_brick_controller.active_position_change
                if position_change is None:
                    position_info = 'Unknown position'
                else:
                    position_info = str(position_change)

            head_brick = scanner_brick.head_brick.resolve_parent()
            head_port = bricks.brick_port(head_brick)
            head_brick_controller = bricks_controllers.brick_controller(head_brick, resolve_parent=False)

            def try_value(n):
                try:
                    return head_brick_controller.value(n)
                except:
                    return None

            sensor_values = tuple((try_value(i) for i in range(8)))

            texts.append('  Propulsion(' + propulsion_port + ': ' + position_info + '),' +
                         ' Head(' + head_port + ': ' + str(sensor_values) + ')')

        index = itertools.count()
        tag = self.TAG_BRICKS_INFO
        self.canvas.delete(self.TAG_BRICKS_INFO)
        for text in texts:
            self.canvas.create_text(10, 10 + index.__next__() * 15, anchor=NW, text=text, tags=tag)
