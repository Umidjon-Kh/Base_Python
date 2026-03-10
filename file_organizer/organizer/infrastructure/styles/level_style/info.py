from typing import Dict, Any

# Project modules
from .base import LevelStyle


class InfoStyle(LevelStyle):
    """
    Style for INFO level.
    By default, shows only level, message, and time.
    """

    __slots__ = ()

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
