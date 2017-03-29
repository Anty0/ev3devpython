from utils.runtime_config import RuntimeConfig
from .config import CONFIG_VALUES


class LineFollowerSharedData:
    def __init__(self, config: dict = None):
        from hardware.pilot import PILOT
        from hardware.scanner_reflect import SCANNER_REFLECT
        from hardware.scanner_distance import SCANNER_DISTANCE

        if not PILOT.is_connected or not SCANNER_REFLECT.head_connected:
            raise Exception('LineFollower requires wheels and color sensor at last.')

        self.pilot = PILOT
        self.scanner_reflect = SCANNER_REFLECT
        self.scanner_distance = SCANNER_DISTANCE

        self.config = RuntimeConfig(config_map=CONFIG_VALUES, config_modifications=config)

    def reset(self):
        pass
