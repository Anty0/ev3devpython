from utils.calc import dimensions as dp
from utils.hardware.brick.active_bricks_info_provider import ActiveBricksInfoProvider


class BrickPosition:
    def get(self, active_bricks_info_provider: ActiveBricksInfoProvider or None) -> dp.Position:
        pass


class AbsoluteBrickPosition(BrickPosition):
    def __init__(self, position: dp.Position):
        self._position = position

    def get(self, active_bricks_info_provider: ActiveBricksInfoProvider or None):
        return self._position


class RelativeBrickPosition(BrickPosition):
    def __init__(self, position: dp.Position, from_brick,
                 gear_rotation: dp.Angle = None, gear_ratio: float = 1):
        self._position = position
        self._parent = from_brick

        self._gear_rotation = gear_rotation
        self._gear_ratio = gear_ratio

    def get(self, active_bricks_info_provider: ActiveBricksInfoProvider or None) -> dp.Position:
        parent_position = self._parent.position.get(active_bricks_info_provider)
        parent_position_change = None if active_bricks_info_provider is None else \
            active_bricks_info_provider.position_change(self._parent)
        if parent_position_change is None:
            return dp.Position(
                self._position.point.copy()
                    .rotate(parent_position.angle)
                    .move(parent_position.point),
                self._position.angle.copy()
                    .rotate(parent_position.angle)
            )

        return dp.Position(
            self._position.point.copy()
                .rotate(parent_position.angle)
                .rotate(parent_position_change.rotation)
                .move(parent_position.point)
                .move(parent_position_change.move_vector.copy()
                      .rotate(parent_position.angle)),
            self._position.angle.copy()
                .rotate(parent_position.angle)
                .rotate(parent_position_change.rotation)
        )
