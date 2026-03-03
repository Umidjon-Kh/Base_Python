from json import load, JSONDecodeError
from pathlib import Path
from typing import Dict, Optional
# Project modules
from ..exceptions import PathError, ConfigError


class Loader:
    """
    Loads content os JSON file and returns if in dict format to:
    1) RuleManager: to load all custom user rules
    2) LogManager: to load all styles format
    3) ConfigManager: to load all config params for all managers and returns them
    """

    STYLES = Path(__file__).parent.parent.parent / 'configs' / 'default_styles.json'
    RULES = Path(__file__).parent.parent.parent / 'configs' / 'default_rules.json'
    CONFIG = Path(__file__).parent.parent.parent / 'configs' / 'default_configs.json'

    @classmethod
    def load_from_json(cls, which: str, custom_path: Optional[str] = None) -> Dict:
        """Loads data from JSON-file (Custom or Default)"""
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
                raise ConfigError('Which one to load data is not defined')
        # Trying to load data
        try:
            with open(path, encoding='utf-8') as file:
                data = load(file)
            # checking data in right format or not
            if not isinstance(data, dict):
                raise ConfigError('File must contain configs in dict format')
            return data
        except (IOError, JSONDecodeError) as exc:
            raise PathError(f'Failed to load data: {exc}')
