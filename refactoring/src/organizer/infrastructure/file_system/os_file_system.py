from pathlib import Path
from shutil import move as shutil_move
from typing import List

# Project modules
from application.ports.file_system import FileSystem
from domain.entities import Directory, FileItem
from domain.exceptions import (
    SourceFileNotFoundError,  # our custom exception (consider renaming later)
    PermissionDeniedError,
    DestinationExistsError,
    FileSystemError,
)


class OSFileSystem(FileSystem):
    """
    Real file system adapter using pathlib and shutil.
    Implements all file operations defined in the FileSystem port.
    All standard I/O exceptions are caught and wrapped into custom exceptions
    defined in domain.exceptions.
    """

    def scan(self, path: Path, recursive: bool = True, ignore_patterns: List[str] = []) -> Directory:
        """
        Recursively scan a directory and build an in-memory tree.

        Args:
            path: Root directory to scan.

        Returns:
            Directory object representing the root with all descendants.

        Raises:
            PermissionDeniedError: if the root directory cannot be read.
            FileSystemError: for other OS-level errors.
        """
        try:
            root = Directory(path)
            self._scan_directory(root, recursive)
            return root
        except PermissionError as exc:
            raise PermissionDeniedError(f'Permission denied while scanning {path}: {exc}') from exc
        except OSError as exc:
            raise FileSystemError(f'OS error while scanning {path}: {exc}') from exc

    def _scan_directory(self, directory: Directory, recursive: bool, ignore_patterns: List[str] = []) -> None:
        """
        Helper method to recursively populate a Directory with its children.

        Args:
            directory: Directory object to populate.

        Raises:
            FileSystemError: if an unexpected OS error occurs (except PermissionError).
        """
        try:
            for child_path in directory.path.iterdir():
                # Check if the child should be ignored
                if self._is_ignored(child_path, ignore_patterns):
                    continue

                if child_path.is_file():
                    # FileItem automatically registers itself with the parent directory.
                    FileItem(child_path, directory)
                elif child_path.is_dir():
                    sub_dir = Directory(child_path, directory)
                    # if recursive mode is on, continune scanning deeper
                    if recursive:
                        self._scan_directory(sub_dir, recursive)
                    # otherwise, subdir remains empty (only created)
        except PermissionError:
            # Skip directories we cannot read – this is not considered an error.
            pass
        except OSError as exc:
            # Propagate any other OS error as a generic file system error.
            raise FileSystemError(f'Error while iterating {directory.path}: {exc}') from exc

    def _is_ignored(self, path: Path, ignore_patterns: List[str]) -> bool:
        """Returns True if the path matches any of the ignore patterns"""
        if not ignore_patterns:
            return False
        # Convert path to string relative to the root? We'll just match the full path.
        # But patterns like "*.tmp" should match filenames. path.match works with relative patterns.
        # We'll try to match both the full path and the name.
        for pattern in ignore_patterns:
            if path.match(pattern) or path.name == pattern:
                return True
        return False

    def move(self, file_item: FileItem, destination: Path, parent_dir: Directory, dry_run: bool) -> None:
        """
        Move a file from source to destination.
        If destination already exists, a unique name is generated (e.g., file_(1).txt).

        Args:
            source: Source file path.
            destination: Desired destination path.
            parent_dir: Directory instance to add new child for dir in new path
            dry_run: Only changes path and dels from pareny children not moves from source to dest

        Raises:
            SourceFileNotFoundError: if source does not exist.
            PermissionDeniedError: if lacking permissions.
            FileSystemError: for other OS errors.
        """
        try:
            if not file_item.path.exists():
                raise SourceFileNotFoundError(f'Source file does not exist: {file_item.path}')

            destination.parent.mkdir(parents=True, exist_ok=True)
            final_dest = self._resolve_conflict(destination)
            shutil_move(str(file_item.path), str(final_dest))
            if not dry_run:
                file_item.move_file(final_dest, parent_dir)
        except PermissionError as exc:
            raise PermissionDeniedError(f'Permission denied while moving {file_item} -> {destination}: {exc}') from exc
        except OSError as exc:
            raise FileSystemError(f'OS error while moving {file_item} -> {destination}: {exc}') from exc

    def _resolve_conflict(self, path: Path) -> Path:
        """
        If a file already exists at the given path, generate a new unique path
        by appending `_(n)` before the extension.

        Args:
            path: The desired path.

        Returns:
            A path that does not currently exist.
        """
        if not path.exists():
            return path
        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        counter = 1
        while True:
            new_name = f"{stem}_({counter}){suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1

    def mkdir(self, path: Path, parents: bool = True) -> None:
        """
        Create a directory. If parents=True, also create missing parent directories.

        Args:
            path: Directory path to create.
            parents: Whether to create parent directories as needed.

        Raises:
            PermissionDeniedError: if lacking permissions.
            DestinationExistsError: if the directory already exists (should not happen with exist_ok=True).
            FileSystemError: for other OS errors.
        """
        try:
            path.mkdir(parents=parents, exist_ok=True)
        except PermissionError as exc:
            raise PermissionDeniedError(f'Permission denied creating directory {path}: {exc}') from exc
        except FileExistsError as exc:
            # exist_ok=True should prevent this, but just in case.
            raise DestinationExistsError(f'Directory already exists: {path}') from exc
        except OSError as exc:
            raise FileSystemError(f'OS error creating directory {path}: {exc}') from exc

    def rmdir(self, dir: Directory, dry_run: bool) -> None:
        """
        Remove an empty directory.

        Args:
            path: Directory path to remove.
            dry_run: Only cremoves intanse from parent child list not removes from source

        Raises:
            SourceFileNotFoundError: if the directory does not exist.
            FileSystemError: if the directory is not empty or another OS error occurs.
        """
        try:
            if not dry_run:
                dir.path.rmdir()

        except FileNotFoundError as exc:
            raise SourceFileNotFoundError(f'Directory not found: {dir.path}') from exc
        except OSError as exc:
            if exc.errno == 39:  # Directory not empty
                raise FileSystemError(f'Directory not empty: {dir.path}') from exc
            raise FileSystemError(f'OS error removing directory {dir.path}: {exc}') from exc
        # If everthing is okey juust remove it from parents children list
        dir.rm_dir()

    def exists(self, path: Path) -> bool:
        """
        Check if a path exists.

        Args:
            path: Path to check.

        Returns:
            True if the path exists, False otherwise.

        Raises:
            PermissionDeniedError: if permissions prevent checking.
            FileSystemError: for other OS errors.
        """
        try:
            return path.exists()
        except PermissionError as exc:
            raise PermissionDeniedError(f'Permission denied checking existence of {path}: {exc}') from exc
        except OSError as exc:
            raise FileSystemError(f'OS error checking existence of {path}: {exc}') from exc

    def is_file(self, path: Path) -> bool:
        """
        Check if a path is a regular file.

        Args:
            path: Path to check.

        Returns:
            True if path is a file, False otherwise.

        Raises:
            PermissionDeniedError: if permissions prevent checking.
            FileSystemError: for other OS errors.
        """
        try:
            return path.is_file()
        except PermissionError as exc:
            raise PermissionDeniedError(f'Permission denied checking is_file for {path}: {exc}') from exc
        except OSError as exc:
            raise FileSystemError(f'OS error checking is_file for {path}: {exc}') from exc

    def is_dir(self, path: Path) -> bool:
        """
        Check if a path is a directory.

        Args:
            path: Path to check.

        Returns:
            True if path is a directory, False otherwise.

        Raises:
            PermissionDeniedError: if permissions prevent checking.
            FileSystemError: for other OS errors.
        """
        try:
            return path.is_dir()
        except PermissionError as exc:
            raise PermissionDeniedError(f'Permission denied checking is_dir for {path}: {exc}') from exc
        except OSError as exc:
            raise FileSystemError(f'OS error checking is_dir for {path}: {exc}') from exc
