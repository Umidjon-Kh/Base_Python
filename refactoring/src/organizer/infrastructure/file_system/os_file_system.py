from pathlib import Path
from shutil import move as shutil_move

# Project modules
from application.ports.file_system import FileSystem
from domain.entities import Directory, FileItem


class OSFileSystem(FileSystem):
    """Real file system implementation using pathlib and shutil."""

    def scan(self, path: Path) -> Directory:
        root = Directory(path)
        self._scan_recursive(root)
        return root

    def _scan_recursive(self, directory: Directory) -> None:
        try:
            for child_path in directory.path.iterdir():
                if child_path.is_file():
                    FileItem(child_path, directory)
                elif child_path.is_dir():
                    sub_dir = Directory(child_path, directory)
                    self._scan_recursive(sub_dir)
        except PermissionError:
            pass

    def move(self, source: Path, destination: Path) -> None:
        """
        Move a file from source to destination.
        If destination already exists, generates a new unique name.
        """
        destination.parent.mkdir(parents=True, exist_ok=True)
        final_dest = self._resolve_conflict(destination)
        shutil_move(str(source), str(final_dest))

    def _resolve_conflict(self, path: Path) -> Path:
        """
        If the given path already exists, generate a new path with a suffix _(n).
        Returns the first non‑existing path.
        """
        if not path.exists():
            return path
        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        counter = 1
        while True:
            new_name = f'{stem}_({counter}){suffix}'
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1

    def mkdir(self, path: Path, parents: bool = True) -> None:
        path.mkdir(parents=parents, exist_ok=True)

    def rmdir(self, path: Path) -> None:
        path.rmdir()

    def exists(self, path: Path) -> bool:
        return path.exists()

    def is_file(self, path: Path) -> bool:
        return path.is_file()

    def is_dir(self, path: Path) -> bool:
        return path.is_dir()
