"""
Integration tests using bootstrap().
Tests the full pipeline: ConfigOverrides -> bootstrap() -> OrganizeResult.
Real files, real filesystem — no mocks.
"""

import json
import pytest
from pathlib import Path
from typing import Optional

from ..bootstrap import bootstrap, ConfigOverrides
from ..application import OrganizeResult
from ..exceptions import ConfigValidationError


# ── Helpers ───────────────────────────────────────────────────────────────────


def make_files(directory: Path, names: list) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for name in names:
        (directory / name).write_text('dummy')


def write_config(path: Path, source: Path, dest: Path, extra: Optional[dict] = None) -> Path:
    """Write a minimal config.json. File logging disabled to avoid path=None error."""
    data = {
        'source_dir': str(source),
        'dest_dir': str(dest),
        'dry_run': False,
        'recursive': False,
        'ignore_patterns': [],
        'rules': {'rules_cfg': None, 'rules_repo': None, 'combine': False},
        'styles': {'styles': None, 'styles_repo': None, 'combine': False},
        'logging': {'console': {'enabled': False, 'level': 'DEBUG'}, 'file': {'enabled': False}},
    }
    if extra:
        data.update(extra)
    path.write_text(json.dumps(data))
    return path


def write_rules(path: Path, other_behavior: str = 'ignore') -> Path:
    rules = {
        'other_behavior': other_behavior,
        'ignore_extensions': [],
        'ignore_size_more_than': None,
        'ignore_size_less_than': None,
        'rules': [
            {'type': 'extension', 'extensions': ['.txt'], 'folder': 'Docs', 'priority': 0},
            {'type': 'extension', 'extensions': ['.jpg'], 'folder': 'Images', 'priority': 0},
        ],
    }
    path.write_text(json.dumps(rules))
    return path


# ── Tests ─────────────────────────────────────────────────────────────────────


def test_bootstrap_moves_files_to_correct_folders(tmp_path):
    """Full pipeline moves .txt and .jpg to correct subfolders."""
    source = tmp_path / 'source'
    dest = tmp_path / 'dest'
    make_files(source, ['doc.txt', 'photo.jpg', 'script.py'])

    config_path = write_config(tmp_path / 'config.json', source, dest)
    rules_path = write_rules(tmp_path / 'rules.json')

    result: OrganizeResult = bootstrap(
        ConfigOverrides(
            config_files=config_path,
            rules_file=rules_path,
        )
    )

    assert (dest / 'Docs' / 'doc.txt').exists()
    assert (dest / 'Images' / 'photo.jpg').exists()
    assert not (source / 'doc.txt').exists()  # moved away
    assert result.success
    assert len(result.moved) == 2
    assert len(result.skipped) == 1  # script.py ignored


def test_bootstrap_dry_run_does_not_move(tmp_path):
    """dry_run=True: result shows moved files but no physical move occurs."""
    source = tmp_path / 'source'
    dest = tmp_path / 'dest'
    make_files(source, ['doc.txt', 'photo.jpg'])

    config_path = write_config(tmp_path / 'config.json', source, dest)
    rules_path = write_rules(tmp_path / 'rules.json')

    result: OrganizeResult = bootstrap(
        ConfigOverrides(
            config_files=config_path,
            rules_file=rules_path,
            dry_run=True,
        )
    )

    assert result.dry_run is True
    assert len(result.moved) == 2
    assert (source / 'doc.txt').exists()  # still in source
    assert not (dest / 'Docs' / 'doc.txt').exists()  # not moved


def test_bootstrap_layer3_source_overrides_layer2(tmp_path):
    """source_dir in ConfigOverrides (Layer 3) overrides the one in config.json (Layer 2)."""
    source1 = tmp_path / 'source1'
    source2 = tmp_path / 'source2'
    dest = tmp_path / 'dest'
    make_files(source1, ['file1.txt'])
    make_files(source2, ['file2.txt'])

    config_path = write_config(tmp_path / 'config.json', source1, dest)
    rules_path = write_rules(tmp_path / 'rules.json')

    bootstrap(
        ConfigOverrides(
            config_files=config_path,
            rules_file=rules_path,
            source_dir=source2,  # Layer 3 override
        )
    )

    assert (dest / 'Docs' / 'file2.txt').exists()
    assert not (dest / 'Docs' / 'file1.txt').exists()


def test_bootstrap_inline_rules_cfg(tmp_path):
    """rules_cfg in ConfigOverrides is used instead of rules file."""
    source = tmp_path / 'source'
    dest = tmp_path / 'dest'
    make_files(source, ['script.py'])

    config_path = write_config(tmp_path / 'config.json', source, dest)

    inline_rules = {
        'other_behavior': 'ignore',
        'ignore_extensions': [],
        'ignore_size_more_than': None,
        'ignore_size_less_than': None,
        'rules': [
            {'type': 'extension', 'extensions': ['.py'], 'folder': 'Python', 'priority': 0},
        ],
    }

    result: OrganizeResult = bootstrap(
        ConfigOverrides(
            config_files=config_path,
            rules_cfg=inline_rules,
        )
    )

    assert (dest / 'Python' / 'script.py').exists()
    assert len(result.moved) == 1


def test_bootstrap_missing_source_dir_raises(tmp_path):
    """ConfigValidationError is raised when source_dir is None in all layers."""
    dest = tmp_path / 'dest'
    config = {
        'source_dir': None,
        'dest_dir': str(dest),
        'dry_run': False,
        'recursive': False,
        'ignore_patterns': [],
        'rules': {'rules_cfg': None, 'rules_repo': None, 'combine': False},
        'styles': {'styles': None, 'styles_repo': None, 'combine': False},
        'logging': {'console': {'enabled': False}, 'file': {'enabled': False}},
    }
    config_path = tmp_path / 'config.json'
    config_path.write_text(json.dumps(config))

    with pytest.raises(ConfigValidationError):
        bootstrap(ConfigOverrides(config_files=config_path))


def test_bootstrap_console_level_override(tmp_path):
    """console_level in ConfigOverrides patches the logging config."""
    source = tmp_path / 'source'
    dest = tmp_path / 'dest'
    source.mkdir()

    config_path = write_config(tmp_path / 'config.json', source, dest)
    rules_path = write_rules(tmp_path / 'rules.json')

    # Should not raise — just verifies that logging override is accepted
    result: OrganizeResult = bootstrap(
        ConfigOverrides(
            config_files=config_path,
            rules_file=rules_path,
            console_level='ERROR',
        )
    )
    assert result is not None
