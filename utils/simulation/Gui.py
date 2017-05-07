from tkinter import *

from utils.simulation.world import World


class WorldGui(Tk):
    def __init__(self, world: World):
        super().__init__()
        self.world = world

        self.wm_title("World")
        self.configure(background='white')

        self.canvas_map = Canvas(self, width=self.world.world_map.width,
                                 height=self.world.world_map.height, bg="white")
        self.canvas_map.pack()

        self.canvas_robot = Canvas(self, width=self.world.world_map.width,
                                   height=self.world.world_map.height, bg="transparent")
        self.canvas_robot.pack()

        self._draw_map()
        self._draw_effects()  # TODO: automatically refresh effects
        self.mainloop()

    def _draw_map(self):
        self.canvas_map.delete("all")
        world_map = self.world.world_map
        for x in range(world_map.width):
            for y in range(world_map.height):
                color_rgb = [str(hex(color)) for color in world_map.color_rgb(x, y)]
                self.canvas_map.create_line(x, y, x, y, fill='black' if world_map.wall(x, y) else
                '#%s%s%s' % (color_rgb[0], color_rgb[1], color_rgb[2]))

    def _draw_effects(self):
        self.canvas_robot.delete("all")
        for effect, driver in self.world.effects:
            effect.draw(self.world, driver, self.canvas_robot)
