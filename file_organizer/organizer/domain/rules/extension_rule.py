from typing import List

# Project modules
from ..entities import FileItem
from .rule import Rule


class ExtensionRule(Rule):
    """Matches files by extension and returns a fixed folder segment."""

    def __init__(self, extensions: List[str], folder: str):
        """
        Args:
            extensions: List of extensions (with or without leading dot).
            folder: Target folder name.
        """
        self.extensions = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' for ext in extensions]
        self.folder = folder

    @property
    def priority(self) -> int:
        return 0

    def match(self, file_item: FileItem) -> bool:
        return file_item.suffix.lower() in self.extensions

    def target_segments(self, file_item: FileItem) -> List[str]:
        return [self.folder]
