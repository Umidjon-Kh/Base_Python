from pathlib import Path
import re
from shutil import move as shutil_move
from typing import List, Optional

# Project modules
from ...application import FileSystem
from ...domain import Directory, FileItem
from ...exceptions import (
    SourceFileNotFoundError,
    PermissionDeniedError,
    DestinationExistsError,
    FileSystemError,
)


class OSFileSystem(FileSystem):
    """
    Real file system adapter using pathlib and shutil.
    All I/O exceptions are caught and wrapped into custom exceptions.
    """

    def scan(self, path: Path, recursive: bool = False, ignore_patterns: Optional[List[str]] = None) -> Directory:
        """
        Scan a directory and build an in‑memory tree.
        """
        try:
            root = Directory(path)
            self._scan_directory(root, recursive, ignore_patterns or [])
            return root
        except PermissionError as exc:
            raise PermissionDeniedError(f'Permission denied while scanning {path}: {exc}') from exc
        except OSError as exc:
            raise FileSystemError(f'OS error while scanning {path}: {exc}') from exc

    def _scan_directory(self, directory: Directory, recursive: bool, ignore_patterns: List[str]) -> None:
        """
        Recursively populate a directory with its children.
        """
        try:
            for child_path in directory.path.iterdir():
                if self._is_ignored(child_path, ignore_patterns):
                    continue

                if child_path.is_file():
                    # FileItem constructor automatically registers with parent
                    FileItem(child_path, directory)
                elif child_path.is_dir():
                    sub_dir = Directory(child_path, directory)
                    if recursive:
                        self._scan_directory(sub_dir, recursive, ignore_patterns)
        except PermissionError:
            # Skip directories we cannot read – not an error
            pass
        except OSError as exc:
            raise FileSystemError(f'Error while iterating {directory.path}: {exc}') from exc

    def _is_ignored(self, path: Path, patterns: List[str]) -> bool:
        """Return True if the path matches any ignore pattern."""
        if not patterns:
            return False
        for pattern in patterns:
            if path.match(pattern) or path.name == pattern:
                return True
        return False

    def move(self, file_item: FileItem, destination: Path, new_parent: Directory, dry_run: bool) -> None:
        """
        Move a file. If dry_run is True, no physical move is performed.
        After a successful move, the file_item's location is updated.
        """
        try:
            if not file_item.path.exists():
                raise SourceFileNotFoundError(f'Source file does not exist: {file_item.path}')

            destination.parent.mkdir(parents=True, exist_ok=True)
            final_dest = self._resolve_conflict(destination)

            if not dry_run:
                shutil_move(str(file_item.path), str(final_dest))
                file_item.update_location(final_dest, new_parent)
            else:
                # In dry run, we may still want to update the tree to simulate the move.
                # But for consistency, we'll keep the tree unchanged.
                pass

        except PermissionError as exc:
            raise PermissionDeniedError(
                f'Permission denied while moving {file_item.path} -> {destination}: {exc}'
            ) from exc
        except OSError as exc:
            raise FileSystemError(f'OS error while moving {file_item.path} -> {destination}: {exc}') from exc

    def _resolve_conflict(self, path: Path) -> Path:
        """
        If a file already exists at the given path, generate a new unique name
        by appending `_(n)` before the extension.
        """
        if not path.exists():
            return path
        stem = re.sub(r'(_\(\d+\))+$', '', path.stem)
        suffix = path.suffix
        parent = path.parent

        pattern = re.compile(rf'^{re.escape(stem)}_\((\d+)\){re.escape(suffix)}$')
        max_n = 0
        for entry in parent.iterdir():
            match = pattern.match(entry.name)
            if match:
                max_n = max(max_n, int(match.group(1)))

        return parent / f'{stem}_({max_n + 1}){suffix}'

    def mkdir(self, path: Path, parents: bool = True) -> None:
        try:
            path.mkdir(parents=parents, exist_ok=True)
        except PermissionError as exc:
            raise PermissionDeniedError(f'Permission denied creating directory {path}: {exc}') from exc
        except FileExistsError as exc:
            raise DestinationExistsError(f'Directory already exists: {path}') from exc
        except OSError as exc:
            raise FileSystemError(f'OS error creating directory {path}: {exc}') from exc

    def rmdir(self, directory: Directory, dry_run: bool) -> None:
        """
        Remove an empty directory. If dry_run is True, no physical removal is performed.
        After successful removal, the directory is detached from its parent.
        """
        try:
            if not dry_run:
                directory.path.rmdir()
                directory.remove_from_parent()
        except FileNotFoundError as exc:
            raise SourceFileNotFoundError(f'Directory not found: {directory.path}') from exc
        except OSError as exc:
            if exc.errno == 39:  # Directory not empty
                raise FileSystemError(f'Directory not empty: {directory.path}') from exc
            raise FileSystemError(f'OS error removing directory {directory.path}: {exc}') from exc

    def exists(self, path: Path) -> bool:
        try:
            return path.exists()
        except PermissionError as exc:
            raise PermissionDeniedError(f'Permission denied checking existence of {path}: {exc}') from exc
        except OSError as exc:
            raise FileSystemError(f'OS error checking existence of {path}: {exc}') from exc

    def is_file(self, path: Path) -> bool:
        try:
            return path.is_file()
        except PermissionError as exc:
            raise PermissionDeniedError(f'Permission denied checking is_file for {path}: {exc}') from exc
        except OSError as exc:
            raise FileSystemError(f'OS error checking is_file for {path}: {exc}') from exc

    def is_dir(self, path: Path) -> bool:
        try:
            return path.is_dir()
        except PermissionError as exc:
            raise PermissionDeniedError(f'Permission denied checking is_dir for {path}: {exc}') from exc
        except OSError as exc:
            raise FileSystemError(f'OS error checking is_dir for {path}: {exc}') from exc
