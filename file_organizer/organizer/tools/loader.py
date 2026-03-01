import json
from pathlib import Path
from typing import Dict, Optional

# Project modules
from ..src import PathError, ConfigError


class Loader:
    """
    Loads content of json file and returns it in dict format to:
    1) RuleManager: to load custom user rules
    2) LogManager: to load custom user log formats
    3) ConfigManager: to load custom user configs for organizer
    """

    STYLES = Path(__file__).parent.parent / 'configs' / 'default_styles.json'
    RULES = Path(__file__).parent.parent / 'configs' / 'default_rules.json'
    CONFIG = Path(__file__).parent.parent / 'configs' / 'default_config.json'

    @classmethod
    def load_from_file(cls, which: str, custom_path: Optional[str] = None) -> Dict:
        """Loads data from file (Custom or Default)"""
        # Checking custom path is not None and exists or not
        if custom_path is not None:
            path = Path(custom_path).resolve()
            if not path.exists():
                raise PathError(f'{path.name} is not exists: {path}')
        else:
            if which == 'styles':
                path = cls.STYLES
            elif which == 'rules':
                path = cls.RULES
            elif which == 'config':
                path = cls.CONFIG
            else:
                path = cls.CONFIG
        # Trying to load data
        try:
            with open(path, encoding='utf-8') as file:
                data = json.load(file)
            # Checking data in right type or not
            if not isinstance(data, dict):
                raise ConfigError('File must contain dict format config')
            return data
        except (IOError, json.JSONDecodeError) as exc:
            raise PathError(f'Failed to load data: {exc}')
