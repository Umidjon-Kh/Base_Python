# domain/entities/file_item.py
from __future__ import annotations
from pathlib import Path
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .directory import Directory


class FileItem:
    """
    Represents a single file in the file system.
    Size is fetched lazily when needed (not at creation).
    """

    __slots__ = ('_path', '_name', '_parent', '_stem', '_suffix', '_size', '_size_fetched')

    def __init__(self, path: Path, parent: Directory):
        # Use private attributes to enforce immutability (except size)
        object.__setattr__(self, '_path', path)
        object.__setattr__(self, '_parent', parent)
        object.__setattr__(self, '_size', None)
        object.__setattr__(self, '_size_fetched', False)
        self._post_init()
        # Automatically register with parent directory
        parent.add_child(self)

    def _post_init(self):
        """Normalize and validate attributes."""
        if not isinstance(self._path, Path):
            object.__setattr__(self, '_path', Path(self._path))

        object.__setattr__(self, '_name', self._path.name)
        object.__setattr__(self, '_stem', self._path.stem)
        object.__setattr__(self, '_suffix', self._path.suffix)

        # Consistency check
        expected_name = self._stem + self._suffix
        if self._name != expected_name:
            object.__setattr__(self, '_name', expected_name)

    @property
    def path(self) -> Path:
        return self._path

    @property
    def name(self) -> str:
        return self._name

    @property
    def parent(self) -> Optional[Directory]:
        return self._parent

    @property
    def stem(self) -> str:
        return self._stem

    @property
    def suffix(self) -> str:
        return self._suffix

    @property
    def size(self) -> Optional[int]:
        if not self._size_fetched:
            try:
                stat = self._path.stat()
                object.__setattr__(self, '_size', stat.st_size)
            except OSError:
                object.__setattr__(self, '_size', None)
            object.__setattr__(self, '_size_fetched', True)
        return self._size

    def move_file(self, path: Path, parent: Directory) -> None:
        object.__setattr__(self, '_path', path)
        self._parent.del_child(self)
        object.__setattr__(self, '_parent', parent)
        parent.add_child(self)

    def __repr__(self) -> str:
        return f'FileItem(name={self.name})'

    def info(self) -> str:
        return (
            f'File: {self.name}'
            f'\n\tsize: {self.size}\n\tparent: {self.parent.name if self.parent else None}\n\tpath: {self.path}'
        )
