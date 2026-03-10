from typing import Dict, Any

# Project modules
from .base import LevelStyle


class ErrorStyle(LevelStyle):
    """
    Style for ERROR level.
    By default, uses red color for level and message.
    """

    __slots__ = ()

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
