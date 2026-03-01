from typing import Dict, Any, Tuple

# Project modules
from ..src import ConfigError


class ConfigNormalizer:
    """Normalizes data, config of Managers and Returns it in right format"""

    @classmethod
    def data_normalizer(cls, data: Dict[str, Any], mg: str) -> Dict[str, Any]:
        """Returns right format of config for Config Manager"""
        normalized = {}
        for key, value in data.items():
            if mg == 'rule_mg':
                value = cls.rule_mg(value)
            if mg == 'config_mg':
                key, value = cls.config_mg(key, value)
            if mg == 'log_mg':
                if not isinstance(value, dict):
                    raise ConfigError('Unacceptable type of log handler value, value must be type(dict)')
                key, value = cls.log_mg(key, value)

            normalized[key] = value
        return normalized

    @staticmethod
    def rule_mg(value: str) -> str:
        """Returns right format of rules for Rule Manager"""
        value = value.lower()
        if not value.startswith('.'):
            value = '.' + value
        return value

    @staticmethod
    def config_mg(key: str, value: Any) -> Tuple[str, Any]:
        """Returns right format of config for Config Manager"""
        boolean_args = ('dry_run', 'recursive', 'clean_source', 'combine')
        if key in boolean_args and not isinstance(value, bool):
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            else:
                raise ConfigError(f'Value of {key} must be boolean type (true/false)')
        return key, value

    @staticmethod
    def log_mg(key: str, value: Dict[str, Any]) -> Tuple[str, Dict]:
        """Returns validated and right formated config for Log Manager"""
        # Validating console log handler configs
        if key == 'console' and value.get('enabled', True):
            # Checking for unacceptable params
            for param in value.keys():
                if param not in ('level', 'colorize', 'style', 'style_data', 'style_path'):
                    raise ConfigError(f'Logger Configuration param "{param}" is unacceptable')

        # Validating file_log handler configs
        elif key == 'file' and value.get('enabled', False):
            # Chacking for unacceptale params
            for param in value.keys():
                if param not in (
                    'level',
                    'style',
                    'style_data',
                    'style_path',
                    'path',
                    'rotation',
                    'retention',
                    'compression',
                ):
                    raise ConfigError(f'Logger Configuration param "{param}" is unacceptable')
            # Checking file path added or not
            if not value.get('path'):
                raise ConfigError('File logger enabled but not \'path\' specified')
        else:
            raise ConfigError('Logger Configuration unacceptable sink config')
        return key, value
