from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

# Project modules
from domain.entities import Directory, FileItem


class FileSystem(ABC):
    """
    Port for file system operations.
    Any adapter (real OS, test mock, remote FS) must implement this.
    """

    @abstractmethod
    def scan(self, path: Path, recursive: bool = True, ignore_patterns: List[str] = []) -> Directory:
        """
        Scan a directory and build an in-memory tree.
        If recursive=False, only immediate children are scanned.
        ignore_patterns: list of glob patterns to exclude from scanning.
        """
        pass

    @abstractmethod
    def move(self, file_item: FileItem, destination: Path, parent_dir: Directory, dry_run: bool) -> None:
        """
        Move a file from source to destination.
        And some rules if it exists you can do your own rules if dublicates
        """
        pass

    @abstractmethod
    def mkdir(self, path: Path, parents: bool = True) -> None:
        """Create a directory. If parents=True, create missing parents."""
        pass

    @abstractmethod
    def rmdir(self, dir: Directory, dry_run: bool) -> None:
        """Remove an empty directory. Should raise if not empty."""
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
