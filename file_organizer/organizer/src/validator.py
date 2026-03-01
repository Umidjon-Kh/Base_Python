from typing import Any, Dict

# Porject modules
from .exceptions import ConfigError


# Class to Validate all Configs
class ConfigValidator:
    """Validates all configs off other Classes"""

    @staticmethod
    def validate_logging_config(config: Dict[str, Any]) -> Dict:
        """Validating reqiured fields nd types"""
        # Validating console configuration params
        if 'console' in config and config['console'].get('enabled', True):
            # Checking for unacceptable params
            for param in config['console'].keys():
                if param not in ('level', 'colorize', 'style', 'style_data', 'style_path'):
                    raise ConfigError(f'Logger Configuration param "{param}" is unacceptable')

        # Validating file_log configuration params
        if 'file' in config and config['file'].get('enabled', False):
            # Checking for unacceptable params
            for param in config['file'].keys():
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
            if config['file'].get('path', None):
                raise ConfigError('File logger enabled but not \'path\' specified')
        # If it doesnt gets config we just return dict
        return config or {}
