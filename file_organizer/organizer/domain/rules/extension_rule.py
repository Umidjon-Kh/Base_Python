from typing import List, Optional

# Project modules
from ..entities import FileItem
from .rule import Rule


class ExtensionRule(Rule):
    """Matches files by extension and returns a fixed folder segment."""

    __slots__ = ('_priority', 'extensions', 'folder')

    def __init__(self, extensions: List[str], folder: str, priority: Optional[int] = 0):
        """
        Args:
            extensions: List of extensions (with or without leading dot).
            folder: Target folder name.
        """
        self.extensions = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' for ext in extensions]
        self.folder = folder
        self._priority = priority if priority is not None else 0

    @property
    def priority(self) -> int:
        return self._priority

    def match(self, file_item: FileItem) -> bool:
        return file_item.suffix.lower() in self.extensions

    def target_segments(self, file_item: FileItem) -> List[str]:
        return [self.folder]
