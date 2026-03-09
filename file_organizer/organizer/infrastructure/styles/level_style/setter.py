from typing import Dict

# Project modules
from ....application import StyleSetter
from .base import LevelStyle
from .debug import DebugStyle
from .info import InfoStyle
from .warning import WarningStyle
from .error import ErrorStyle
from .critical import CriticalStyle
from ....exceptions import StyleNotFoundError


class StyleSet(StyleSetter):
    __slots__ = ('_styles',)

    def __init__(self, styles: Dict[str, LevelStyle]) -> None:
        # Default styles for all levels (with empty config = defaults)
        default_styles = {
            'debug': DebugStyle({}),
            'info': InfoStyle({}),
            'warning': WarningStyle({}),
            'error': ErrorStyle({}),
            'critical': CriticalStyle({}),
        }
        # Merge: user styles override defaults
        self._styles = {**default_styles, **{k.lower(): v for k, v in styles.items()}}

    def get_style(self, target: str) -> LevelStyle:
        """
        Return style for the given level name (case-insensitive).
        """
        level_name = target
        key = level_name.lower()
        if key not in self._styles:
            # This should never happen because we have defaults, but just in case
            raise StyleNotFoundError(f'No style found for level: {level_name}')
        return self._styles[key]
