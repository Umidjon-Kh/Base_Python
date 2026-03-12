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
        super().__init__(config)
