# application/ports/file_system.py
from abc import ABC, abstractmethod
from pathlib import Path

# Project modules
from domain.entities import Directory


class FileSystem(ABC):
    """
    Port for file system operations.
    Any adapter (real OS, test mock, remote FS) must implement this.
    """

    @abstractmethod
    def scan(self, path: Path) -> Directory:
        """
        Recursively scan a directory and build an in-memory tree.
        Returns the root Directory entity with all descendants.
        """
        pass

    @abstractmethod
    def move(self, source: Path, destination: Path) -> None:
        """Move a file from source to destination. And some ruls if it exits you can do youw own rules if dublicate"""
        pass

    @abstractmethod
    def mkdir(self, path: Path, parents: bool = True) -> None:
        """Create a directory. If parents=True, create missing parents."""
        pass

    @abstractmethod
    def rmdir(self, path: Path) -> None:
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
