from typing import Dict, Any

# Project modules
from ...application.ports import StyleRepository
from .level_styles import (
    LevelStyle,
    StyleSet,
    DebugStyle,
    InfoStyle,
    WarningStyle,
    ErrorStyle,
    CriticalStyle,
)
from ...domain.exceptions import UnknownStyleType


class InMemoryStyleRepository(StyleRepository):
    """
    Builds a StyleSet from an in-memory dictionary.
    Useful for tests or for providing styles via CLI.

    The input dictionary should have the same structure as a JSON file:
    keys are level names ('debug', 'info', 'warning', 'error', 'critical'),
    values are configuration dicts for each level.
    Unknown level names will raise UnknownStyleType.
    """

    __slots__ = ('_config',)

    def __init__(self, config: Dict[str, Dict[str, Any]]) -> None:
        """
        Args:
            config: Dictionary with level names as keys and style configs as values.
        """
        self._config = config.copy()

    def load_styles(self) -> StyleSet:
        """
        Convert the stored config dictionary into a StyleSet.

        Returns:
            StyleSet instance containing styles for all configured levels.

        Raises:
            UnknownStyleType: if any key in config is not one of the five standard levels.
        """
        style_instances: Dict[str, LevelStyle] = {}

        for level_name, level_config in self._config.items():
            style = self._create_style(level_name, level_config)
            style_instances[level_name] = style

        # StyleSet will merge these with its own defaults for missing levels
        return StyleSet(style_instances)

    def _create_style(self, level_name: str, config: Dict[str, Any]) -> LevelStyle:
        """
        Factory method to create a specific LevelStyle instance based on level name.

        Args:
            level_name: One of 'debug', 'info', 'warning', 'error', 'critical'.
            config: Configuration dictionary for that level (may be empty).

        Returns:
            An instance of the corresponding LevelStyle subclass.

        Raises:
            UnknownStyleType: if level_name is not recognized.
        """
        if level_name == 'debug':
            return DebugStyle(config)
        elif level_name == 'info':
            return InfoStyle(config)
        elif level_name == 'warning':
            return WarningStyle(config)
        elif level_name == 'error':
            return ErrorStyle(config)
        elif level_name == 'critical':
            return CriticalStyle(config)
        else:
            raise UnknownStyleType(f'Unknown level name: {level_name}')
