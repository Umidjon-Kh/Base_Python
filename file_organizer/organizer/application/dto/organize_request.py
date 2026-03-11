from pathlib import Path
from typing import List, Optional

# Project module: RuleSetter
from ...domain import RuleSet


class OrganizeRequest:
    """
    What the use case needs to do.

    Assembled by the use case itself from config_repo and rule_repo.
    Immutable after creation - nobody should change it mid-execution.
    """

    __slots__ = (
        '_source_dir',
        '_dest_dir',
        '_rule_set',
        '_dry_run',
        '_recursive',
        '_ignore_patterns',
    )

    def __init__(
        self,
        source_dir: Path,
        dest_dir: Optional[Path],
        rule_set: RuleSet,
        dry_run: bool = False,
        recursive: bool = True,
        ignore_patterns: Optional[List[str]] = None,
    ) -> None:
        self._source_dir = source_dir
        self._dest_dir = dest_dir
        self._rule_set = rule_set
        self._dry_run = dry_run
        self._recursive = recursive
        self._ignore_patterns = ignore_patterns or []

    @property
    def source_dir(self) -> Path:
        return self._source_dir

    @property
    def dest_dir(self) -> Optional[Path]:
        return self._dest_dir

    @property
    def rule_set(self) -> RuleSet:
        return self._rule_set

    @property
    def dry_run(self) -> bool:
        return self._dry_run

    @property
    def recursive(self) -> bool:
        return self._recursive

    @property
    def ignore_patterns(self) -> List[str]:
        return self._ignore_patterns

    def __repr__(self) -> str:
        return (
            f'OrganizeRequest('
            f'source_dir={self._source_dir!r}, '
            f'dest_dir={self._dest_dir!r}, '
            f'dry_run={self._dry_run!r}, '
            f'recursive={self._recursive!r})'
        )
