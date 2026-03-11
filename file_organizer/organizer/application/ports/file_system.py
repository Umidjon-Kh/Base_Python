from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

# Project modules
from ...domain.entities import Directory, FileItem


class FileSystem(ABC):
    """
    Port for file system operations.
    Any adapter (real OS, test mock, remote FS) must implement this.
    """

    @abstractmethod
    def scan(self, path: Path, recursive: bool = False, ignore_patterns: Optional[List[str]] = None) -> Directory:
        """
        Scan a directory and build an in‑memory tree.
        If recursive=False, only immediate children are scanned.
        ignore_patterns: list of glob patterns to exclude from scanning.
        Returns the root Directory entity with all descendants.
        """
        pass

    @abstractmethod
    def move(self, file_item: FileItem, destination: Path, new_parent: Directory, dry_run: bool) -> None:
        """
        Move a file from its current location to the destination.
        If destination already exists, a unique name is generated (e.g., file_(1).txt).
        After a successful move, the file_item's location is updated in the tree via update_location().
        If dry_run is True, no physical move is performed; only the tree may be updated (depending on design).
        """
        pass

    @abstractmethod
    def mkdir(self, path: Path, parents: bool = True) -> None:
        """Create a directory. If parents=True, create missing parents."""
        pass

    @abstractmethod
    def rmdir(self, directory: Directory, dry_run: bool) -> None:
        """
        Remove an empty directory. After successful removal, the directory is detached from its parent.
        If dry_run is True, no physical removal is performed; the tree may still be updated (depending on design).
        """
        pass

    @abstractmethod
    def exists(self, path: Path) -> bool:
        """Check if a path exists."""
        pass

    @abstractmethod
    def is_file(self, path: Path) -> bool:
        """Check if path is a file."""
        pass

    @abstractmethod
    def is_dir(self, path: Path) -> bool:
        """Check if path is a directory."""
        pass
