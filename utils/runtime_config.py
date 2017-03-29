from .log import get_logger

log = get_logger(__name__)


class RuntimeConfig:
    def __init__(self, config_map: dict = None, config_modifications: dict = None):
        self._config_map = config_map if config_map is not None else {}
        self._config = {}
        self._update_config(config_modifications)

        self._listeners_on_config_whole_change = []
        self._listeners_on_config_value_change = []

    def _update_config(self, config: dict = None):
        if config is None:
            config = {}

        for name, info in self._config_map.items():
            if name not in config:
                config[name] = self._config[name] if name in self._config else info['default_value']
            else:
                config[name] = self._convert_config_value(name, config[name])

        self._config = config

    def _convert_config_value(self, name: str, value):
        value_type = self._config_map[name]['type']
        converted_value = value
        if value_type == 'str' or value_type == 'string':
            converted_value = str(value)
        elif value_type == 'int' or value_type == 'integer':
            converted_value = int(value)
        elif value_type == 'float':
            converted_value = float(value)
        elif value_type == 'bool' or value_type == 'boolean':
            if isinstance(value, str):
                if value == 'true' or value == 'True':
                    value = True
                elif value == 'false' or value == 'False':
                    value = False
            converted_value = bool(value)
        elif value_type == 'enum':
            converted_value = self._config_map[name]['enum_options'][str(value)]
        log.debug('Setting value of ' + str(value_type) + ' ' + str(name)
                  + ' to ' + str(value) + ' as ' + str(type(converted_value)) + ' ' + str(converted_value))
        return converted_value

    def update_config(self, config: dict = None):
        self._update_config(config)
        self.on_config_whole_change()

    def extract_config_values(self, *keys: str) -> dict:
        result = {}
        for name in keys:
            result[name] = self._config[name]
        return result

    def update_extracted_config(self, config: dict):
        for name in config.keys():
            config[name] = self._config[name]

    def set_config_value(self, name: str, value):
        if name not in self._config:
            log.error('Can\'t set config value \'' + name + '\'. No config value with given name exists.')
            return False

        self._config[name] = self._convert_config_value(name, value)
        self.on_config_value_change(name, value)
        return True

    def get_config_value(self, name):
        # if name not in self._config:
        #     log.error('Can\'t get config value \'' + name + '\'. No config value with given name exists.')
        #     return None

        return self._config[name]

    def add_on_config_whole_change_listener(self, listener: callable):
        with self._listeners_on_config_whole_change:
            self._listeners_on_config_whole_change.append(listener)

    def remove_on_config_whole_change_listener(self, listener: callable):
        with self._listeners_on_config_whole_change:
            self._listeners_on_config_whole_change.remove(listener)

    def add_on_config_value_change_listener(self, listener: callable):
        with self._listeners_on_config_value_change:
            self._listeners_on_config_value_change.append(listener)

    def remove_on_config_value_change_listener(self, listener: callable):
        with self._listeners_on_config_value_change:
            self._listeners_on_config_value_change.remove(listener)

    def on_config_whole_change(self):
        for listener in self._listeners_on_config_whole_change:
            listener()

    def on_config_value_change(self, name: str, new_value):
        for listener in self._listeners_on_config_value_change:
            listener(name, new_value)
