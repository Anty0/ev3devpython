import time
from threading import Thread

from tkinter import *

from utils.calc.color import argb_to_str
from utils.graphics.drawer import CanvasDrawer
from utils.hardware.brick.active_bricks_info_provider import ActiveBricksInfoProvider
from utils.hardware.brick.bricks import Bricks
from utils.hardware.simulation.world import World


class WorldGui(Tk):
    TAG_MAP = 'map'
    TAG_ROBOT = 'robot'

    def __init__(self, world: World, active_bricks_info_provider: ActiveBricksInfoProvider or None, bricks: Bricks):
        super().__init__()
        self.world = world
        self.active_bricks_info_provider = active_bricks_info_provider
        self.bricks = bricks

        self.wm_title("World")
        self.configure(background='white')

        self.canvas = Canvas(self, width=self.world.map.width,
                             height=self.world.map.height, bg="white")
        self.canvas.pack()
        self.robot_canvas_drawer = CanvasDrawer(self.canvas, self.TAG_ROBOT)

        self.draw_thread = Thread(target=self._draw_thread_loop, name='WorldGuiDrawThread', daemon=True)

        self._draw_map()
        self._draw_bricks()

    def mainloop(self, n=0):
        self.draw_thread.start()
        super().mainloop(n=n)

    def _draw_thread_loop(self):
        while True:
            self._draw_bricks()
            time.sleep(0.2)

    def _draw_map(self):
        self.canvas.delete(self.TAG_MAP)
        world_map = self.world.map
        for x in range(world_map.width):
            for y in range(world_map.height):
                color_rgb = world_map.color_rgb(x, y)
                color_str = 'black' if world_map.wall(x, y) else argb_to_str(color_rgb[0], color_rgb[1], color_rgb[2])
                self.canvas.create_line(x, y, x + 1, y + 1, fill=color_str, tags=self.TAG_MAP)

    def _draw_bricks(self):
        self.robot_canvas_drawer.clear()
        for brick in self.bricks.tuple_bricks:
            brick.draw_2d(self.world, self.active_bricks_info_provider, self.robot_canvas_drawer)
