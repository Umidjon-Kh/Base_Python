from pathlib import Path
from typing import Optional, List, Dict, Any

# Project module: exceptions
from ...exceptions import PathIsNotAbsoluteError


class AppConfig:
    """
    Application configuration object.

    Holds all settings required to run the file organizer.
    All paths are stored as absolute Path objects.
    The configuration is immutable after creation.

    Rules and styles can be provided in two ways (mutually exclusive):
        _file  — path to a JSON file  (JsonRuleRepository / JsonStyleRepository)
        _cfg   — inline dict          (InMemoryRuleRepository / InMemoryStyleRepository)
    bootstrap() decides which adapter to create based on which one is not None.
    If both are provided, _cfg takes priority (more specific overrides less specific).
    """

    __slots__ = (
        '_source_dir',
        '_dest_dir',
        '_dry_run',
        '_recursive',
        '_ignore_patterns',
        '_rules_file',
        '_rules_cfg',
        '_styles_file',
        '_styles_cfg',
        '_logging',
    )

    def __init__(
        self,
        source_dir: Path,
        dest_dir: Path,
        dry_run: bool = False,
        recursive: bool = True,
        ignore_patterns: Optional[List[str]] = None,
        rules_file: Optional[Path] = None,
        rules_cfg: Optional[Dict[str, Any]] = None,
        styles_file: Optional[Path] = None,
        styles_cfg: Optional[Dict[str, Any]] = None,
        logging: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._source_dir = source_dir
        self._dest_dir = dest_dir
        self._dry_run = dry_run
        self._recursive = recursive
        self._ignore_patterns = ignore_patterns
        self._rules_file = rules_file
        self._rules_cfg = rules_cfg
        self._styles_file = styles_file
        self._styles_cfg = styles_cfg
        self._logging = logging
        self._post_init()

    def _post_init(self) -> None:
        """Validate the configuration after initialization."""
        # Path checks
        if not self._source_dir.is_absolute():
            raise PathIsNotAbsoluteError(f'source_dir must be absolute, got {self._source_dir}')
        if self._dest_dir is not None and not self._dest_dir.is_absolute():
            raise PathIsNotAbsoluteError(f'dest_dir must be absolute, got {self._dest_dir}')
        if self._rules_file is not None and not self._rules_file.is_absolute():
            raise PathIsNotAbsoluteError(f'rules_file must be absolute, got {self._rules_file}')
        if self._styles_file is not None and not self._styles_file.is_absolute():
            raise PathIsNotAbsoluteError(f'styles_file must be absolute, got {self._styles_file}')

        # Type checks
        if not isinstance(self._dry_run, bool):
            raise ValueError(f'dry_run must be a boolean, got {type(self._dry_run)}')
        if not isinstance(self._recursive, bool):
            raise ValueError(f'recursive must be a boolean, got {type(self._recursive)}')

        # ignore_patterns: None or list of strings
        if self._ignore_patterns is not None:
            if not isinstance(self._ignore_patterns, list):
                raise ValueError('ignore_patterns must be a list or None')
            for pat in self._ignore_patterns:
                if not isinstance(pat, str):
                    raise ValueError(f'ignore pattern must be string, got {type(pat)}')

        # rules_cfg and styles_cfg must be dicts if provided
        if self._rules_cfg is not None and not isinstance(self._rules_cfg, dict):
            raise ValueError(f'rules_cfg must be a dict, got {type(self._rules_cfg)}')
        if self._styles_cfg is not None and not isinstance(self._styles_cfg, dict):
            raise ValueError(f'styles_cfg must be a dict, got {type(self._styles_cfg)}')

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def source_dir(self) -> Path:
        """Absolute path to the source directory."""
        return self._source_dir

    @property
    def dest_dir(self) -> Path:
        """Absolute path to the destination root directory."""
        return self._dest_dir

    @property
    def dry_run(self) -> bool:
        """If True, simulate moving without actually moving files."""
        return self._dry_run

    @property
    def recursive(self) -> bool:
        """If True, scan source directory recursively."""
        return self._recursive

    @property
    def ignore_patterns(self) -> Optional[List[str]]:
        """List of glob patterns to ignore during scanning."""
        return self._ignore_patterns

    @property
    def rules_file(self) -> Optional[Path]:
        """Absolute path to JSON file with sorting rules, or None."""
        return self._rules_file

    @property
    def rules_cfg(self) -> Optional[Dict[str, Any]]:
        """Inline rules config dict, or None."""
        return self._rules_cfg

    @property
    def styles_file(self) -> Optional[Path]:
        """Absolute path to JSON file with logging styles, or None."""
        return self._styles_file

    @property
    def styles_cfg(self) -> Optional[Dict[str, Any]]:
        """Inline styles config dict, or None."""
        return self._styles_cfg

    @property
    def logging(self) -> Optional[Dict[str, Any]]:
        """Raw logging configuration dictionary."""
        return self._logging

    def __repr__(self) -> str:
        return (
            f'AppConfig('
            f'source_dir={self._source_dir!r}, '
            f'dest_dir={self._dest_dir!r}, '
            f'dry_run={self._dry_run!r}, '
            f'recursive={self._recursive!r}, '
            f'ignore_patterns={self._ignore_patterns!r}, '
            f'rules_file={self._rules_file!r}, '
            f'rules_cfg={self._rules_cfg!r}, '
            f'styles_file={self._styles_file!r}, '
            f'styles_cfg={self._styles_cfg!r}, '
            f'logging={self._logging!r})'
        )
