from .log import get_logger

log = get_logger(__name__)


class RuntimeConfig:
    def __init__(self, default_values: dict = None, config_modifications: dict = None):
        self._default_values = default_values
        self._config = {}
        self._update_config(config_modifications)

    def _update_config(self, config: dict = None):
        if config is None:
            config = {}

        for name, info in self._default_values.items():
            if name not in config:
                config[name] = self._config[name] if name in self._config else info['default_value']
            else:
                config[name] = self._convert_config_value(name, config[name])

        self._config = config

    def _convert_config_value(self, name: str, value):
        value_type = self._default_values[name]['type']
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
            converted_value = self._default_values[name]['enum_options'][str(value)]
        log.debug('Setting value of ' + str(value_type) + ' ' + str(name)
                  + ' to ' + str(value) + ' as ' + str(type(converted_value)) + ' ' + str(converted_value))
        return converted_value

    def update_config(self, config: dict = None):
        self._update_config(config)
        self.on_config_change()

    def set_config_value(self, name: str, value):
        if name not in self._config:
            log.error('Can\'t set config value \'' + name + '\'. No config value with given name exists.')
            return False

        self._config[name] = self._convert_config_value(name, value)
        self.on_config_value_change(name, value)
        return True

    def get_config_value(self, name):
        if name not in self._config:
            log.error('Can\'t get config value \'' + name + '\'. No config value with given name exists.')
            return None

        return self._config[name]

    def on_config_change(self):
        pass

    def on_config_value_change(self, name: str, new_value):
        pass
