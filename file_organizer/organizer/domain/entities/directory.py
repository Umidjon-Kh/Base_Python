from __future__ import annotations
from pathlib import Path
from typing import List, Union, Optional, Generator, Dict

# Project modules
from .file_item import FileItem


class Directory:
    """
    Represents a directory in the file system.
    Can contain files (FileItem) and subdirectories (Directory).
    Maintains a tree structure via parent/child references.
    """

    __slots__ = ('_path', '_children', '_parent', '_size_cache')

    def __init__(self, path: Union[Path, str], parent: Optional[Directory] = None):
        """
        Initialize a Directory.

        Args:
            path: Path to the directory.
            parent: Parent directory (None for root).
        """
        if not isinstance(path, Path):
            path = Path(path)
        object.__setattr__(self, '_path', path)
        object.__setattr__(self, '_children', [])
        object.__setattr__(self, '_parent', parent)
        object.__setattr__(self, '_size_cache', None)  # lazy cache for total size
        if parent:
            parent.add_child(self)

    @property
    def path(self) -> Path:
        """Absolute path of the directory."""
        return self._path

    @property
    def name(self) -> str:
        """Directory name."""
        return self._path.name

    @property
    def parent(self) -> Optional[Directory]:
        """Parent directory."""
        return self._parent

    @property
    def children(self) -> List[Union[FileItem, Directory]]:
        """Return a copy of children list to prevent external mutation."""
        return self._children.copy()

    def remove_from_parent(self) -> None:
        """
        Detach this directory from its parent.
        Called after physical deletion to keep the in‑memory tree consistent.
        """
        if self._parent:
            self._parent.del_child(self)
            object.__setattr__(self, '_parent', None)

    def add_child(self, child: Union[FileItem, Directory]) -> None:
        """Add a child (file or subdirectory) to this directory."""
        self._children.append(child)
        # Invalidate size cache because total size may have changed
        object.__setattr__(self, '_size_cache', None)

    def del_child(self, child: Union[FileItem, Directory]) -> bool:
        """
        Remove a child from the children list.
        Returns True if the child was found and removed, False otherwise.
        """
        for i, c in enumerate(self._children):
            if c is child:
                del self._children[i]
                object.__setattr__(self, '_size_cache', None)
                return True
        return False

    def get_child(self, name: str) -> Optional[Union[FileItem, Directory]]:
        """
        Find a direct child by its name (either file name or directory name).
        Returns None if not found.
        """
        for child in self._children:
            if child.name == name:
                return child
        return None

    def find(self, name: str, recursive: bool = False) -> Optional[Union[FileItem, Directory]]:
        """
        Find a file or directory by name. If recursive=False, search only direct children.
        If recursive=True, search recursively.
        Returns the first matching entity or None.
        """
        if not recursive:
            return self.get_child(name)
        # Recursive search
        for child in self._children:
            if child.name == name:
                return child
            if isinstance(child, Directory):
                result = child.find(name, recursive=True)
                if result is not None:
                    return result
        return None

    def find_all(self, name: str) -> Dict[Directory, Union[FileItem, Directory]]:
        """
        Recursively find all entities (files or directories) with the given name.
        Returns a dictionary mapping parent directory to the found entity.
        """
        results = {}
        for child in self._children:
            if child.name == name:
                results[self] = child
            if isinstance(child, Directory):
                results.update(child.find_all(name))
        return results

    def is_empty(self) -> bool:
        """Return True if this directory has no children."""
        return len(self._children) == 0

    def walk_files(self) -> Generator[FileItem, None, None]:
        """
        Recursively yield all FileItem objects in this directory tree.
        """
        for child in self._children:
            if isinstance(child, FileItem):
                yield child
            elif isinstance(child, Directory):
                yield from child.walk_files()

    @property
    def size(self) -> Optional[int]:
        """
        Total size of all files in this directory and its subdirectories (bytes).
        Cached after first calculation; cache is invalidated when children change.
        Returns None if any file size is unavailable.
        """
        if self._size_cache is None:
            total = 0
            for child in self._children:
                if isinstance(child, FileItem):
                    child_size = child.size
                    if child_size is None:
                        # If one file size is unavailable, total size is unknown
                        object.__setattr__(self, '_size_cache', None)
                        return None
                    total += child_size
                elif isinstance(child, Directory):
                    child_size = child.size
                    if child_size is None:
                        object.__setattr__(self, '_size_cache', None)
                        return None
                    total += child_size
            object.__setattr__(self, '_size_cache', total)
        return self._size_cache

    def __repr__(self) -> str:
        return f'Directory(name={self.name}, children={len(self._children)})'

    def info(self) -> str:
        """Return a human‑readable string with directory details."""
        return (
            f'Directory: {self.name}\n'
            f'\tparent: {self.parent.name if self.parent else None}\n'
            f'\tsize: {self.size}\n'
            f'\tchildren count: {len(self._children)}'
        )
