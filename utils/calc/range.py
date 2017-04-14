from utils.utils import crop_m


class Range:
    def __init__(self, min_val: float, max_val: float):
        self._val_min = min_val
        self._val_max = max_val
        self._val_diff = max_val - min_val

    @property
    def val_min(self):
        return self._val_min

    @property
    def val_max(self):
        return self._val_max

    @property
    def val_diff(self):
        return self._val_diff

    def crop(self, val):
        return crop_m(val, self._val_min, self._val_max)

    def to_percent(self, val):
        return (val - self._val_min) / self._val_diff * 100

    def range(self, step: int = 1):
        return range(int(self._val_min), int(self._val_max), step)

    def generate_json_info(self):
        return {
            'val_min': self._val_min,
            'val_max': self._val_max,
            'val_diff': self._val_diff
        }
