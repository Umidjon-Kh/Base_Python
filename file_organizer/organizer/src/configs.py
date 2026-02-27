import json
from pathlib import Path
from typing import Any, Dict, Optional
from .exceptions import ConfigError


class ConfigManager:
    """Manages all Configs of Organizer"""

    __slots__ = ('__configs',)

    DEFAULT_CONFIGS_FILE = Path(__file__).parent.parent / 'configs' / 'deafult_configs.json'

    # Initializing configs
    def __init__(self, config_path: Path) -> None:
        """
        Initializes configs dict and
        calls methods to load and normalizes all data in config dict
        """
        self.__configs = {}

    # Normalizing configs from dict
    @staticmethod
    def normalize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """Returns right format of dict of configs"""
        boolean_args = ['']
        normalized = {}
        for key, value in data.items():


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
                normalized = 