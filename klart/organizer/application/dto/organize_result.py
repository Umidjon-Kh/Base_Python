from pathlib import Path
from typing import List, Tuple


class OrganizeResult:
    """
    What the use case did.

    Returned by use_case.execute() to the caller (CLI, GUI, tests).
    Mutable - use case fills it incrementally as it processes each file.

    Fields:
        moved   - list of (source_path, dest_path) tuples
        skipped - list of source_path that were skipped (ignored by rules)
        errors  - list of (source_path, error_message) tuples
        dry_run - whether this was a simulation run
    """

    __slots__ = (
        '_moved',
        '_skipped',
        '_removed',
        '_errors',
        '_dry_run',
        '_recursive',
        '_clean_mode',
    )

    def __init__(
        self,
        dry_run: bool = False,
        recursive: bool = False,
        clean_mode: bool = False,
    ) -> None:
        self._moved: List[Tuple[Path, Path]] = []
        self._skipped: List[Path] = []
        self._removed: List[Path] = []
        self._errors: List[Tuple[Path, str]] = []
        self._dry_run: bool = dry_run
        self._recursive: bool = recursive
        self._clean_mode: bool = clean_mode

    # Mutating methods (use case calls these)

    def add_moved(self, source: Path, dest: Path) -> None:
        self._moved.append((source, dest))

    def add_skipped(self, source: Path) -> None:
        self._skipped.append(source)

    def add_error(self, source: Path, message: str) -> None:
        self._errors.append((source, message))

    def add_removed(self, source: Path) -> None:
        self._removed.append(source)

    # Read-only properties

    @property
    def moved(self) -> List[Tuple[Path, Path]]:
        return self._moved

    @property
    def skipped(self) -> List[Path]:
        return self._skipped

    @property
    def removed(self) -> List[Path]:
        return self._removed

    @property
    def errors(self) -> List[Tuple[Path, str]]:
        return self._errors

    @property
    def dry_run(self) -> bool:
        return self._dry_run

    @property
    def recursive(self) -> bool:
        return self._recursive

    @property
    def clean_mode(self) -> bool:
        return self._clean_mode

    @property
    def total_files(self) -> int:
        return len(self._moved) + len(self._skipped) + len(self._errors)

    @property
    def success(self) -> bool:
        return len(self._errors) == 0

    def __repr__(self) -> str:
        return (
            f'OrganizeResult('
            f'moved={len(self._moved)}, '
            f'skipped={len(self._skipped)}, '
            f'removed={len(self._removed)}, '
            f'errors={len(self._errors)}, '
            f'dry_run={self._dry_run!r}, '
            f'recursive={self._recursive!r}, '
            f'clean_mode={self._clean_mode!r} '
        )
