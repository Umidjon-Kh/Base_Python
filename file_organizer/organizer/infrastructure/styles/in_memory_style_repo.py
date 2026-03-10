from copy import deepcopy
from typing import Dict, Any, Optional

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
from ...exceptions import UnknownStyleType, StyleFormatError


class InMemoryStyleRepository(StyleRepository):
    """
    Builds a StyleSet from an in-memory dictionary.
    Useful for tests or for providing styles via CLI.

    The input dictionary should have the same structure as a JSON file:
    keys are level names ('debug', 'info', 'warning', 'error', 'critical'),
    values are configuration dicts for each level.
    Unknown level names will raise UnknownStyleType.
    """

    __slots__ = ('styles_data', 'styles_file', 'default_repo', 'combine')

    def __init__(
        self,
        styles_data: Optional[Dict[str, Dict[str, Any]]] = None,
        styles_repo: Optional[StyleRepository] = None,
        default_repo: Optional[StyleRepository] = None,
        combine: bool = False,
    ) -> None:
        """
        Args:
            styles_g: Dictionary with level names as keys and style configs as values.
            default_repo: Repository to load default styles from (if combine=True).
            combine: If True, merge default styles with provided styles cfg
        """
        self.styles_data = styles_data
        self.styles_file = styles_repo
        self.default_repo = default_repo
        self.combine = combine

    def load_styles(self) -> StyleSet:
        styles_data = {}
        if self.combine and self.default_repo:
            styles_data = self.default_repo.load_styles().styles
            # If user styles-file is not None
            if self.styles_file is not None:
                # Deep merging user styles and default styles
                user_styles = self.styles_file.load_styles().styles
                styles_data = self._deep_merge(styles_data, user_styles)
            if self.styles_data is not None:
                # Deep merging styles data and styles_data
                styles_data = self._deep_merge(styles_data, self.styles_data)
            # Building styles from merged styles_data
            styles = self._build_styles_from_dict(styles_data)
            # Returning StyleSet
            return StyleSet(styles)
        else:
            if self.styles_file is not None:
                styles_data = self.styles_file.load_styles().styles
                if self.styles_data is not None:
                    styles_data = self._deep_merge(styles_data, self.styles_data)
            # Building styles from styles_data
            styles = self._build_styles_from_dict(styles_data)
            # Returning StyleSet
            return StyleSet(styles)

    def _deep_merge(self, non_priority_dict: Dict, priority_dict: Dict) -> Dict:
        """Returns recursively deep merged dict"""
        base = deepcopy(non_priority_dict)
        # Iterating dict items if item value is dict calling to recursively copy deep_merge
        for key, value in priority_dict.items():
            # if both values are dict type
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                base[key] = self._deep_merge(base[key], value)
            else:
                # Otherwise, overwrite the value in base dict
                base[key] = value

        return base

    def _build_styles_from_dict(self, styles_data: Dict[str, Any]) -> Dict[str, LevelStyle]:
        if not isinstance(styles_data, dict):
            raise StyleFormatError('\'styles\' must be a dict')
        styles: Dict[str, LevelStyle] = {}
        for level, config in styles_data.items():
            style = self._create_style(level, config)
            styles[level] = style
        return styles

    def _create_style(self, level: str, config: Dict[str, Any]) -> LevelStyle:
        """
        Factory method to create a specific LevelStyle instance based on level name.

        Args:
            level: One of 'debug', 'info', 'warning', 'error', 'critical'.
            config: Configuration dictionary for that level (may be empty).

        Returns:
            An instance of the corresponding LevelStyle subclass.

        Raises:
            UnknownStyleType: if level is not recognized.
        """
        if level == 'debug':
            return DebugStyle(config)
        elif level == 'info':
            return InfoStyle(config)
        elif level == 'warning':
            return WarningStyle(config)
        elif level == 'error':
            return ErrorStyle(config)
        elif level == 'critical':
            return CriticalStyle(config)
        else:
            raise UnknownStyleType(f'Unknown level name: {level}')
