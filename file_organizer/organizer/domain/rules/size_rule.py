from typing import Optional, List

# Project modules
from ..entities import FileItem
from .rule import Rule


class SizeRule(Rule):
    """
    Matches files based on size in bytes.
    Returns a fixed folder segment (could be extended to compute dynamic categories).
    """

    def __init__(self, min_size: Optional[int] = None, max_size: Optional[int] = None, folder: str = "Other"):
        """
        At least one of min_size or max_size must be provided.
        """
        if min_size is None and max_size is None:
            raise ValueError('SizeRule requires at least one of min_size or max_size')
        if min_size and max_size and min_size >= max_size:
            raise ValueError('SizeRule max size value must be more than min size value')
        self.min_size = min_size
        self.max_size = max_size
        self.folder = folder

    @property
    def priority(self) -> int:
        return 50

    def match(self, file_item: FileItem) -> bool:
        size = file_item.size
        if size is None:
            return False
        if self.min_size is not None and size < self.min_size:
            return False
        if self.max_size is not None and size > self.max_size:
            return False
        return True

    def target_segments(self, file_item: FileItem) -> List[str]:
        return [self.folder]
