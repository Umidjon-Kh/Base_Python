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
        super().__init__(config)
