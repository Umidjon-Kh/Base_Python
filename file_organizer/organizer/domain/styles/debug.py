from typing import Dict, Any

# Project modules
from .base import LevelStyle


class DebugStyle(LevelStyle):
    """
    Style for DEBUG level.
    By default, shows path, function, and line number in addition to basic info.
    """

    __slots__ = ()

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize DebugStyle with level-specific defaults.
        If config lacks some keys, they are filled from defaults.
        """
        # Defaults specific to DEBUG
        debug_defaults = {
            'show_path': True,
            'show_function': True,
            'show_line': True,
            'level_color': 'cyan',
        }
        # Merge with user config (user values override defaults)
        merged_config = {**debug_defaults, **config}
        super().__init__(merged_config)
