"""
Unit tests for OrganizeFilesUseCase.
Uses fake implementations of all ports — no real filesystem, no real logger.
"""

# import pytest
from pathlib import Path
from typing import List, Optional

from organizer.application import AppConfig
from organizer.application.use_cases import OrganizeFilesUseCase
from organizer.application.ports import FileSystem, Logger
from organizer.domain import FileItem, Directory
from organizer.infrastructure.config import InMemoryConfigRepository
from organizer.infrastructure.rules import JsonRuleRepository
# from organizer.exceptions import RuleNotFoundError


# ── Fake port implementations ─────────────────────────────────────────────────


class FakeLogger(Logger):
    """Collects log calls without printing anything."""

    def __init__(self):
        self.messages: List[str] = []

    def debug(self, msg, *a, **kw):
        self.messages.append(f'DEBUG: {msg}')

    def info(self, msg, *a, **kw):
        self.messages.append(f'INFO: {msg}')

    def warning(self, msg, *a, **kw):
        self.messages.append(f'WARNING: {msg}')

    def error(self, msg, *a, **kw):
        self.messages.append(f'ERROR: {msg}')

    def critical(self, msg, *a, **kw):
        self.messages.append(f'CRITICAL: {msg}')


class FakeFileSystem(FileSystem):
    """
    In-memory fake filesystem.
    Tracks move() calls without touching the real disk.
    scan() returns a pre-built Directory from given FileItem paths.
    """

    def __init__(self, files: List[Path]):
        self._root = Directory(Path('/source'))
        for f in files:
            FileItem(f, self._root)
        self.moved: List[tuple] = []
        self.mkdirs: List[Path] = []

    def scan(self, path, recursive=False, ignore_patterns=None) -> Directory:
        return self._root

    def move(self, file_item, destination, new_parent, dry_run):
        if not file_item.path.exists() and not str(file_item.path).startswith('/source'):
            raise FileNotFoundError(str(file_item.path))
        if not dry_run:
            self.moved.append((file_item.path, destination))

    def mkdir(self, path, parents=True):
        self.mkdirs.append(path)

    def rmdir(self, directory, dry_run):
        pass

    def exists(self, path):
        return False

    def is_file(self, path):
        return False

    def is_dir(self, path):
        return False


def make_config(
    source_dir: Path,
    dest_dir: Optional[Path] = None,
    dry_run: bool = False,
    recursive: bool = False,
) -> AppConfig:
    return AppConfig(
        source_dir=source_dir,
        dest_dir=dest_dir,
        dry_run=dry_run,
        recursive=recursive,
    )


def make_rule_repo(tmp_path: Path, other_behavior: str = 'use_other') -> JsonRuleRepository:
    """Create a JsonRuleRepository with simple extension rules."""
    import json

    cfg = {
        'other_behavior': other_behavior,
        'ignore_extensions': [],
        'ignore_size_more_than': None,
        'ignore_size_less_than': None,
        'rules': [
            {'type': 'extension', 'extensions': ['.txt'], 'folder': 'Docs', 'priority': 0},
            {'type': 'extension', 'extensions': ['.jpg'], 'folder': 'Images', 'priority': 0},
        ],
    }
    path = tmp_path / 'rules.json'
    path.write_text(json.dumps(cfg))
    return JsonRuleRepository(path)


# ── Tests ─────────────────────────────────────────────────────────────────────


def test_use_case_moves_matched_files(tmp_path):
    """Files with matching rules are recorded as moved."""
    source = Path('/source')
    dest = tmp_path / 'dest'

    config_repo = InMemoryConfigRepository(make_config(source, dest))
    rule_repo = make_rule_repo(tmp_path)
    logger = FakeLogger()
    fs = FakeFileSystem([Path('/source/doc.txt'), Path('/source/img.jpg')])

    use_case = OrganizeFilesUseCase(config_repo, rule_repo, fs, logger)
    result = use_case.execute()

    assert len(result.moved) == 2
    assert len(result.skipped) == 0
    assert len(result.errors) == 0
    assert result.success


def test_use_case_skips_unmatched_files_with_ignore_behavior(tmp_path):
    """Files with no matching rule are skipped when other_behavior='ignore'."""
    source = Path('/source')
    dest = tmp_path / 'dest'

    config_repo = InMemoryConfigRepository(make_config(source, dest))
    rule_repo = make_rule_repo(tmp_path, other_behavior='ignore')
    logger = FakeLogger()
    fs = FakeFileSystem([Path('/source/script.py')])

    use_case = OrganizeFilesUseCase(config_repo, rule_repo, fs, logger)
    result = use_case.execute()

    assert len(result.moved) == 0
    assert len(result.skipped) == 1


def test_use_case_dry_run_does_not_call_fs_move(tmp_path):
    """In dry_run mode, fs.move() is still called but file is recorded as moved."""
    source = Path('/source')
    dest = tmp_path / 'dest'

    config_repo = InMemoryConfigRepository(make_config(source, dest, dry_run=True))
    rule_repo = make_rule_repo(tmp_path)
    logger = FakeLogger()
    fs = FakeFileSystem([Path('/source/doc.txt')])

    use_case = OrganizeFilesUseCase(config_repo, rule_repo, fs, logger)
    result = use_case.execute()

    assert result.dry_run is True
    assert len(result.moved) == 1
    assert len(fs.moved) == 0  # FakeFileSystem.move() skips append when dry_run=True


def test_use_case_catches_errors_per_file(tmp_path):
    """An error on one file is recorded and processing continues."""
    source = Path('/source')
    dest = tmp_path / 'dest'

    config_repo = InMemoryConfigRepository(make_config(source, dest))
    rule_repo = make_rule_repo(tmp_path)
    logger = FakeLogger()

    class BrokenFileSystem(FakeFileSystem):
        def move(self, file_item, destination, new_parent, dry_run):
            raise OSError('disk error')

    fs = BrokenFileSystem([Path('/source/doc.txt'), Path('/source/img.jpg')])

    use_case = OrganizeFilesUseCase(config_repo, rule_repo, fs, logger)
    result = use_case.execute()

    assert len(result.errors) == 2
    assert result.success is False


def test_use_case_rule_not_found_goes_to_errors(tmp_path):
    """other_behavior='raise' causes RuleNotFoundError to be recorded in errors."""
    source = Path('/source')
    dest = tmp_path / 'dest'

    config_repo = InMemoryConfigRepository(make_config(source, dest))
    rule_repo = make_rule_repo(tmp_path, other_behavior='raise')
    logger = FakeLogger()
    fs = FakeFileSystem([Path('/source/script.py')])  # no rule for .py

    use_case = OrganizeFilesUseCase(config_repo, rule_repo, fs, logger)
    result = use_case.execute()

    assert len(result.errors) == 1
    assert len(result.moved) == 0


def test_use_case_dest_none_uses_source_as_base(tmp_path):
    """When dest_dir is None, files are organized inside source_dir."""
    source = Path('/source')

    config_repo = InMemoryConfigRepository(make_config(source, dest_dir=None))
    rule_repo = make_rule_repo(tmp_path)
    logger = FakeLogger()
    fs = FakeFileSystem([Path('/source/doc.txt')])

    use_case = OrganizeFilesUseCase(config_repo, rule_repo, fs, logger)
    result = use_case.execute()

    # dest path should be source / 'Docs'
    moved_dest = result.moved[0][1]
    assert str(moved_dest).startswith(str(source))
