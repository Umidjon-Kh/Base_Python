from abc import ABC, abstractmethod
from typing import List

# Project modules
from ..entities import FileItem


class Rule(ABC):
    """
    Base class for all sorting rules.
    Each rule decides whether a file matches and returns a list of path segments
    (folder names) that should be appended to the destination root.
    """

    @property
    @abstractmethod
    def priority(self) -> int:
        """Returns priority level in digit form"""
        pass

    @abstractmethod
    def match(self, file_item: FileItem) -> bool:
        """Check if the file matches this rule."""
        pass

    @abstractmethod
    def target_segments(self, file_item: FileItem) -> List[str]:
        """
        Return a list of path segments (e.g., ['Images', 'SmallSize']).
        This method is called only after a successful match.
        It may use the file item to compute dynamic segments (e.g., size category).
        """
        pass
