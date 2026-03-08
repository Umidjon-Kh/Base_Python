from typing import Dict, Any

# Project modules
from .base import LevelStyle


class InfoStyle(LevelStyle):
    """
    Style for INFO level.
    By default, shows only level, message, and time.
    """

    __slots__ = ()

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize InfoStyle with level-specific defaults.
        """
        info_defaults = {
            'show_path': False,
            'show_function': False,
            'show_line': False,
            'level_color': 'green',
        }
        merged_config = {**info_defaults, **config}
        super().__init__(merged_config)
