from typing import Dict, Any

# Project modules
from .base import LevelStyle


class CriticalStyle(LevelStyle):
    """
    Style for CRITICAL level.
    By default, uses bright red (or 'RED') and shows all details.
    """

    __slots__ = ()

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize CriticalStyle with level-specific defaults.
        """
        critical_defaults = {
            'level_color': 'RED',  # loguru bright red
            'msg_color': 'RED',
            'show_path': True,
            'show_function': True,
            'show_line': True,
        }
        merged_config = {**critical_defaults, **config}
        super().__init__(merged_config)
