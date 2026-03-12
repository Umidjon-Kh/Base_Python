"""
Tests for style repository implementations and StyleSet behavior.
"""

import pytest
import json
from pathlib import Path

from organizer.infrastructure.styles.level_style import (
    DebugStyle,
    InfoStyle,
    WarningStyle,
    ErrorStyle,
    CriticalStyle,
    StyleSet,
)
from organizer.exceptions import UnknownStyleType, StyleFileNotFoundError, StyleFormatError
from organizer.infrastructure.styles import JsonStyleRepository, InMemoryStyleRepository


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def sample_styles_data() -> dict:
    """Raw dict as it would appear in a styles JSON file."""
    return {
        'debug': {'show_icon': True, 'level_icon': '🐞', 'level_color': 'cyan'},
        'info': {'level_color': 'green', 'msg_color': 'white'},
        'warning': {'level_color': 'yellow'},
        'error': {'level_color': 'red', 'show_path': True},
        'critical': {'level_color': 'RED', 'show_line': True},
    }


@pytest.fixture
def styles_file(tmp_path, sample_styles_data) -> Path:
    """Write sample_styles_data to a temp JSON file."""
    path = tmp_path / 'styles.json'
    path.write_text(json.dumps(sample_styles_data))
    return path


@pytest.fixture
def default_repo(styles_file) -> JsonStyleRepository:
    return JsonStyleRepository(styles_file)


# ── StyleSet ──────────────────────────────────────────────────────────────────


def test_styleset_empty_dict_gives_defaults():
    """StyleSet({}) fills all five levels with default LevelStyle objects."""
    style_set = StyleSet({})
    assert isinstance(style_set.get_style('debug'), DebugStyle)
    assert isinstance(style_set.get_style('info'), InfoStyle)
    assert isinstance(style_set.get_style('warning'), WarningStyle)
    assert isinstance(style_set.get_style('error'), ErrorStyle)
    assert isinstance(style_set.get_style('critical'), CriticalStyle)


def test_styleset_user_styles_override_defaults():
    """User-supplied styles replace the corresponding default."""
    custom_debug = DebugStyle({'level_color': 'magenta'})
    style_set = StyleSet({'debug': custom_debug})
    assert style_set.get_style('debug') is custom_debug
    # other levels still default
    assert isinstance(style_set.get_style('info'), InfoStyle)


def test_styleset_unknown_level_raises():
    """get_style with unknown level raises StyleNotFoundError."""
    style_set = StyleSet({})
    with pytest.raises(Exception):
        style_set.get_style('banana')


def test_styleset_case_insensitive():
    """Level name lookup is case-insensitive."""
    style_set = StyleSet({})
    assert isinstance(style_set.get_style('DEBUG'), DebugStyle)
    assert isinstance(style_set.get_style('Warning'), WarningStyle)


# ── JsonStyleRepository ───────────────────────────────────────────────────────


def test_json_repo_loads_all_levels(default_repo):
    """JsonStyleRepository correctly loads all five levels."""
    style_set = default_repo.load_styles()
    for level in ('debug', 'info', 'warning', 'error', 'critical'):
        style_set.get_style(level)  # must not raise


def test_json_repo_missing_file_raises(tmp_path):
    """Loading from non-existent file raises StyleFileNotFoundError."""
    repo = JsonStyleRepository(tmp_path / 'missing.json')
    with pytest.raises(StyleFileNotFoundError):
        repo.load_styles()


def test_json_repo_invalid_json_raises(tmp_path):
    """Corrupted JSON raises StyleFormatError."""
    path = tmp_path / 'bad.json'
    path.write_text('{ not valid }')
    repo = JsonStyleRepository(path)
    with pytest.raises(StyleFormatError):
        repo.load_styles()


def test_json_repo_unknown_level_raises(tmp_path):
    """Unknown level name in JSON raises UnknownStyleType."""
    path = tmp_path / 's.json'
    path.write_text(json.dumps({'banana': {'level_color': 'yellow'}}))
    repo = JsonStyleRepository(path)
    with pytest.raises(UnknownStyleType):
        repo.load_styles()


# ── InMemoryStyleRepository ───────────────────────────────────────────────────


def test_in_memory_no_extras_returns_empty_styleset(default_repo):
    """No styles_data, no styles_repo, combine=False → empty StyleSet (only defaults from StyleSet itself)."""
    repo = InMemoryStyleRepository(default_repo=default_repo, combine=False)
    style_set = repo.load_styles()
    # StyleSet fills defaults so get_style must not raise
    assert isinstance(style_set.get_style('info'), InfoStyle)


def test_in_memory_combine_loads_default_repo(default_repo):
    """combine=True without extras → loaded from default_repo."""
    repo = InMemoryStyleRepository(default_repo=default_repo, combine=True)
    style_set = repo.load_styles()
    # all levels from default_repo available
    for level in ('debug', 'info', 'warning', 'error', 'critical'):
        style_set.get_style(level)


def test_in_memory_styles_data_overrides(default_repo):
    """styles_data replaces corresponding levels in StyleSet."""
    repo = InMemoryStyleRepository(
        default_repo=default_repo,
        styles_data={'debug': {'level_color': 'blue'}},
        combine=True,
    )
    style_set = repo.load_styles()
    assert isinstance(style_set.get_style('debug'), DebugStyle)
    # other levels still from default
    assert isinstance(style_set.get_style('info'), InfoStyle)


def test_in_memory_styles_repo_overrides_default(default_repo, tmp_path):
    """styles_repo replaces levels from default_repo."""
    custom_data = {'warning': {'level_color': 'blue'}}
    custom_path = tmp_path / 'custom.json'
    custom_path.write_text(json.dumps(custom_data))
    custom_repo = JsonStyleRepository(custom_path)

    repo = InMemoryStyleRepository(
        default_repo=default_repo,
        styles_repo=custom_repo,
        combine=True,
    )
    style_set = repo.load_styles()
    assert isinstance(style_set.get_style('warning'), WarningStyle)


def test_in_memory_unknown_level_in_styles_data_raises(default_repo):
    """Unknown key in styles_data raises UnknownStyleType."""
    repo = InMemoryStyleRepository(
        default_repo=default_repo,
        styles_data={'banana': {}},
        combine=False,
    )
    with pytest.raises(UnknownStyleType):
        repo.load_styles()
