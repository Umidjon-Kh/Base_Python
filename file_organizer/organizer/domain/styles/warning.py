from typing import Dict, Any

# Project modules
from .base import LevelStyle


class WarningStyle(LevelStyle):
    """
    Style for WARNING level.
    By default, uses yellow color for level.
    """

    __slots__ = ()

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize WarningStyle with level-specific defaults.
        """
        warning_defaults = {
            'level_color': 'yellow',
            'msg_color': 'yellow',
        }
        merged_config = {**warning_defaults, **config}
        super().__init__(merged_config)
