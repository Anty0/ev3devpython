from utils.calc import dimensions as dp


class PositionChange:
    def __init__(self, rotation: dp.Angle, move_vector: dp.Point):
        self.rotation = rotation
        self.move_vector = move_vector


class ActiveBricksInfoProvider:
    def position_change(self, brick) -> PositionChange or None:
        pass
