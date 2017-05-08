from ev3dev.auto import INPUT_1 as IN_1, INPUT_2 as IN_2, INPUT_3 as IN_3, INPUT_4 as IN_4, \
    OUTPUT_A as OUT_A, OUTPUT_B as OUT_B, OUTPUT_C as OUT_C, OUTPUT_D as OUT_D

from utils.hardware.brick.base import Brick, WheelBrick
from utils.hardware.brick.main_brick import MainBrick


class Bricks:
    def __init__(self, main_brick: MainBrick, *bricks: Brick, **ports: Brick):
        self.main_brick = main_brick
        self.tuple_bricks = tuple(bricks)
        self.ports = {
            IN_1: None, IN_2: None, IN_3: None, IN_4: None,
            OUT_A: None, OUT_B: None, OUT_C: None, OUT_D: None
        }

        for port, port_brick in ports.items():
            if port in self.ports and port_brick in self.tuple_bricks:
                self.ports[port] = port_brick

    def brick_port(self, brick: Brick):
        for port, port_brick in self.ports.items():
            if port_brick == brick:
                return port
        return None

    def wheels_bricks(self) -> tuple:
        return tuple(
            filter(
                lambda brick: isinstance(brick, WheelBrick),
                self.tuple_bricks
            )
        )

    def generate_json_info(self):
        return {}  # TODO: implement
