from __future__ import annotations
from pathlib import Path
from typing import Optional, Union, TYPE_CHECKING

# Project modules
if TYPE_CHECKING:
    from .directory import Directory


class FileItem:
    """
    Represents a single file in the file system.
    Contains only file metadata and a reference to its parent directory.
    Size is fetched lazily from the filesystem when first accessed.
    This class is intentionally kept free of business logic related to sorting or moving.
    """

    __slots__ = ('_path', '_name', '_parent', '_stem', '_suffix', '_size', '_size_fetched')

    def __init__(self, path: Union[Path, str], parent: Directory):
        """
        Initialize a FileItem.

        Args:
            path: Absolute or relative path to the file.
            parent: The Directory object that contains this file.
                   The parent must already have this file as a child.
        """
        # Use object.__setattr__ to bypass any potential __setattr__ override
        # and to keep immutability of most attributes.
        object.__setattr__(self, '_path', path)
        object.__setattr__(self, '_parent', parent)
        object.__setattr__(self, '_size', None)
        object.__setattr__(self, '_size_fetched', False)
        self._post_init()
        # Automatically register with parent directory
        parent.add_child(self)

    def _post_init(self):
        """Normalize and derive name, stem, suffix from path."""
        if not isinstance(self._path, Path):
            object.__setattr__(self, '_path', Path(self._path))

        object.__setattr__(self, '_name', self._path.name)
        object.__setattr__(self, '_stem', self._path.stem)
        object.__setattr__(self, '_suffix', self._path.suffix)

        # Consistency check: stem + suffix should equal name
        expected_name = self._stem + self._suffix
        if self._name != expected_name:
            object.__setattr__(self, '_name', expected_name)

    @property
    def path(self) -> Path:
        """Full path of the file."""
        return self._path

    @property
    def name(self) -> str:
        """File name including extension."""
        return self._name

    @property
    def parent(self) -> Optional[Directory]:
        """Parent directory containing this file."""
        return self._parent

    @property
    def stem(self) -> str:
        """File name without extension."""
        return self._stem

    @property
    def suffix(self) -> str:
        """File extension including the dot."""
        return self._suffix

    @property
    def size(self) -> Optional[int]:
        """
        File size in bytes. Fetched lazily from the filesystem on first access.
        Returns None if the file cannot be accessed (e.g., permission denied).
        """
        if not self._size_fetched:
            try:
                stat = self._path.stat()
                object.__setattr__(self, '_size', stat.st_size)
            except OSError:
                object.__setattr__(self, '_size', None)
            object.__setattr__(self, '_size_fetched', True)
        return self._size

    def update_location(self, new_path: Path, new_parent: Directory) -> None:
        """
        Update the file's location in the in‑memory tree after a move.
        This method should be called by the infrastructure after a successful file move.
        It removes the file from the old parent and adds it to the new one.

        Args:
            new_path: The new absolute path after the move.
            new_parent: The new parent Directory object.
        """
        # Remove from old parent
        if self._parent:
            self._parent.del_child(self)
        # Update attributes
        object.__setattr__(self, '_path', new_path)
        object.__setattr__(self, '_parent', new_parent)
        # Re-derive name, stem, suffix (in case they changed, e.g., conflict resolution)
        object.__setattr__(self, '_name', new_path.name)
        object.__setattr__(self, '_stem', new_path.stem)
        object.__setattr__(self, '_suffix', new_path.suffix)
        # Add to new parent
        new_parent.add_child(self)
        # Invalidate size cache (file may have changed)
        object.__setattr__(self, '_size', None)
        object.__setattr__(self, '_size_fetched', False)

    def __repr__(self) -> str:
        return f'FileItem(name={self.name})'

    def info(self) -> str:
        """Return a human‑readable string with file details."""
        return (
            f'File: {self.name}\n'
            f'\tsize: {self.size}\n'
            f'\tparent: {self.parent.name if self.parent else None}\n'
            f'\tpath: {self.path}'
        )
