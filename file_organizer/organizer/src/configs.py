import json
from pathlib import Path
from typing import Any, Dict, Optional
from .exceptions import ConfigError


class ConfigManager:
    """Manages all Configs of Organizer"""

    __slots__ = ('__configs',)

    DEFAULT_CONFIGS_FILE = Path(__file__).parent.parent / 'configs' / 'deafult_configs.json'

    # Initializing configs
    def __init__(self, config_path: Optional[Path]) -> None:
        """
        Initializes configs dict and
        calls methods to load and normalizes all data in config dict
        """

        # 1.Action: getting defalut configs
        self.load_defaults()
        # 2.Action: if config path is not None
        # Updating config with custom configs
        if config_path:
            self.load_from_file(config_path)

    # Getter for private attr
    @property
    def configs(self) -> Dict:
        """Returns copy of configs"""
        return self.__configs.copy()

    # Normalizing configs from dict
    @staticmethod
    def _normalize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """Returns right format of dict of configs"""
        boolean_args = ('dry_run', 'recursive', 'clean_source', 'combine')
        normalized = {}
        for key, value in data.items():
            if key in boolean_args and not isinstance(value, bool):
                raise ConfigError(f'Value of {key} must be boolean type (true/false)')
            normalized[key] = value
        return normalized

    # Loading configs from file
    def load_from_file(self, file_path: Path) -> None:
        """Loads configs from JSON-file"""
        try:
            with open(file_path, encoding='utf-8') as file:
                data = json.load(file)

                # Checking content from data
                if not isinstance(data, dict):
                    raise ConfigError('File of configs must contain dict')
                # normalizing all config attrs
                normalized = self._normalize_dict(data)
                self.__configs.update(normalized)
        except (IOError, json.JSONDecodeError) as exc:
            raise ConfigError(f'Error while loading configs from:\nFile: {file_path}\nError: {exc}')

    def load_defaults(self) -> None:
        """
        Loads default cinfigs in default_configs.json if it exits
        else loads from basic integrated configs
        """
        default_file = self.DEFAULT_CONFIGS_FILE
        # 1.Scenario: if path file exits
        if default_file.exists():
            self.load_from_file(default_file)
        # 2.Scenario: if not
        else:
            # Integrated configs
            self.__configs.update(
                {
                    'dest': None,
                    'recursive': True,
                    'dry_run': False,
                    'clean_source': True,
                    'rules': None,
                    'rules_file': None,
                    'combine': False,
                    'stream_level': 'debug',
                    'log_file': None,
                    'write_level': 'debug',
                }
            )
