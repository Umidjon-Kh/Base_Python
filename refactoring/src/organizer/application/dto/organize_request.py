from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

# Project modules
from domain.exceptions import InvalidPathError, SourceFileNotFoundError


@dataclass(frozen=True)
class OrganizeRequest:
    """
    Data Transfer Object for the file organization request.
    Contains all parameters passed from the CLI or any other interface.
    """

    source: Path
    dest: Optional[Path] = None
    recursive: bool = False
    dry_run: bool = False
    clean: bool = False
    ignore_patterns: List[str] = []

    def __post_init__(self):
        """Validate the request data."""
        if not self.source.exists():
            raise SourceFileNotFoundError(f'Source path does not exist: {self.source}') from ValueError
        if not self.source.is_dir():
            raise InvalidPathError(f'Source must be a directory: {self.source}') from ValueError
        if not isinstance(self.recursive, bool):
            raise ValueError('Recursive param value must be bool')
        if not isinstance(self.dry_run, bool):
            raise ValueError('Dry run param value must be bool')
        if not isinstance(self.clean, bool):
            raise ValueError('Clean param value must be bool')
