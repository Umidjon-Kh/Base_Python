from typing import Dict, Any

# Project modules
from .base import LevelStyle


class CriticalStyle(LevelStyle):
    """
    Style for CRITICAL level.
    By default, uses bright red (or 'RED') and shows all details.
    """

    __slots__ = ()

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
