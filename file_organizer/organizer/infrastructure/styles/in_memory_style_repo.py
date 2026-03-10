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

    __slots__ = ('styles_cfg', 'default_repo', 'combine')

    def __init__(
        self,
        styles_cfg: Dict[str, Dict[str, Any]],
        default_repo: Optional[StyleRepository] = None,
        combine: bool = False,
    ) -> None:
        """
        Args:
            styles_g: Dictionary with level names as keys and style configs as values.
            default_repo: Repository to load default styles from (if combine=True).
            combine: If True, merge default styles with provided styles cfg
        """
        self.styles_cfg = styles_cfg
        self.default_repo = default_repo
        self.combine = combine

    def load_styles(self) -> StyleSet:
        if self.combine and self.default_repo:
            default_set = self.default_repo.load_styles()
            # Build user styles
            user_styles = self._build_styles_from_dict(self.styles_cfg)
            combined_styles = {**default_set.styles, **user_styles}
            return StyleSet(combined_styles)
        else:
            user_styles = self._build_styles_from_dict(self.styles_cfg)
            return StyleSet(user_styles)

    def _build_styles_from_dict(self, styles_cfg: Dict[str, Any]) -> Dict[str, LevelStyle]:
        if not isinstance(styles_cfg, dict):
            raise StyleFormatError('\'styles\' must be a dict')
        styles: Dict[str, LevelStyle] = {}
        for level, config in styles_cfg.items():
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
