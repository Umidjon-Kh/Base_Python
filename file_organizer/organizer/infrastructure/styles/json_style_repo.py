import json
from pathlib import Path
from typing import Union, Dict, Any

# Project modules
from ...application.ports import StyleRepository
from .level_style import (
    LevelStyle,
    StyleSet,
    DebugStyle,
    InfoStyle,
    WarningStyle,
    ErrorStyle,
    CriticalStyle,
)
from ...exceptions import StyleFileNotFoundError, StyleFormatError, UnknownStyleType


class JsonStyleRepository(StyleRepository):
    """
    Loads styles from a JSON file.

    The JSON file should contain a dictionary with keys 'debug', 'info', 'warning',
    'error', 'critical'. Each key's value is a dictionary of style parameters
    (see LevelStyle for details). Missing levels will be created with defaults
    by StyleSet itself.
    """

    __slots__ = ('_file_path',)

    def __init__(self, file_path: Union[Path, str]) -> None:
        """
        Args:
            file_path: Path to the JSON file.
        """
        self._file_path = file_path if isinstance(file_path, Path) else Path(file_path)

    def load_styles(self) -> StyleSet:
        """
        Read the JSON file and build a StyleSet.

        Returns:
            StyleSet instance.

        Raises:
            StyleFileNotFoundError: if the file does not exist.
            StyleFormatError: if JSON is invalid or not a dictionary.
        """
        if not self._file_path.exists():
            raise StyleFileNotFoundError(f'Styles file not found: {self._file_path}')

        try:
            with open(self._file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except (IOError, json.JSONDecodeError) as exc:
            raise StyleFormatError(f'Invalid JSON in styles file: {exc}') from exc

        if not isinstance(data, dict):
            raise StyleFormatError('Styles file must contain a dictionary')

        # Build style instances for all known levels
        style_instances: Dict[str, LevelStyle] = {}

        for level, style_cfg in data.items():
            level_style = self._create_style(level, style_cfg)
            style_instances[level] = level_style

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
            UnknownStyleType: if level_name is not recognized (shouldn't happen with internal calls).
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
