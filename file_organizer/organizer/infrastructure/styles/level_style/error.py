from typing import Dict, Any

# Project modules
from .base import LevelStyle


class ErrorStyle(LevelStyle):
    """
    Style for ERROR level.
    By default, uses red color for level and message.
    """

    __slots__ = ()

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize ErrorStyle with level-specific defaults.
        """
        error_defaults = {
            'level_color': 'red',
            'msg_color': 'red',
            'show_path': True,
            'show_function': True,
            'show_line': True,
        }
        merged_config = {**error_defaults, **config}
        super().__init__(merged_config)
