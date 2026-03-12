from abc import ABC, abstractmethod
from typing import Any, Dict


class StyleSetter(ABC):
    """
    Base abstract class for all setter like RuleSet and StyleSet
    and methods that should be in all child cls
    """

    __slots__ = ('styles')

    @abstractmethod
    def __init__(self, cfg: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def get_style(self, target) -> Any:
        """Returns target object content"""
        pass
