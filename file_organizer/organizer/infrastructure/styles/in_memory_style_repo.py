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

    __slots__ = ('styles_data', 'styles_repo', 'default_repo', 'combine')

    def __init__(
        self,
        default_repo: StyleRepository,
        styles_data: Optional[Dict[str, Dict[str, Any]]] = None,
        styles_repo: Optional[StyleRepository] = None,
        combine: bool = False,
    ) -> None:
        """
        Args:
            styles_g: Dictionary with level names as keys and style configs as values.
            default_repo: Repository to load default styles from (if combine=True).
            combine: If True, merge default styles with provided styles cfg
        """
        self.default_repo = default_repo
        self.styles_repo = styles_repo
        self.styles_data = styles_data
        self.combine = combine

    def load_styles(self) -> StyleSet:
        """
        Main code for loading and combinig setter and custom user cfg if is not None
        Priority of setter styles attributes
            3 - default styles repository
            2 - custom user styles repository
            1 - custom user config args
        Returns StyleSetter with all combined styles
        """
        # Creating styles data for default styles dict
        styles_data = {}
        # If combine loads default repository styles to styles_data
        if self.combine:
            styles_data = self.default_repo.load_styles().styles
        # if user custom styles repo is not None, updates styles_data
        if self.styles_repo is not None:
            user_styles = self.styles_repo.load_styles().styles
            styles_data.update(user_styles)
        # If user custom styles is not None, updates styles_data
        if self.styles_data is not None:
            # Builds styles from user config
            user_styles = self._build_styles_from_dict(self.styles_data)
            styles_data.update(user_styles)
        # Returning StyleSetter
        return StyleSet(styles_data)

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
