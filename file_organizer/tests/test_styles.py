"""
Tests for style repository implementations and StyleSet behavior.
"""

import pytest
import json
from pathlib import Path

from organizer.domain.styles import (
    # LevelStyle,
    DebugStyle,
    InfoStyle,
    WarningStyle,
    ErrorStyle,
    CriticalStyle,
    StyleSet,
)
from organizer.domain.exceptions import UnknownStyleType, StyleFileNotFoundError, StyleFormatError
from organizer.infrastructure.styles import JsonStyleRepository, InMemoryStyleRepository


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------


@pytest.fixture
def sample_styles_dict() -> dict:
    """Provide a sample styles dictionary for testing."""
    return {
        'debug': {
            'show_icon': True,
            'level_icon': '🐞',
            'level_color': 'cyan',
            'show_path': True,
            'show_function': True,
            'show_line': True,
        },
        'info': {
            'level_color': 'green',
            'msg_color': 'white',
            'time_format': '%Y-%m-%d %H:%M:%S',
        },
        'warning': {
            'level_color': 'yellow',
            'msg_color': 'yellow',
        },
        'error': {
            'level_color': 'red',
            'msg_color': 'red',
            'show_path': True,
            'show_function': True,
        },
        'critical': {
            'level_color': 'RED',  # bright red in loguru
            'msg_color': 'RED',
            'show_path': True,
            'show_function': True,
            'show_line': True,
        },
    }


@pytest.fixture
def temp_styles_file(tmp_path, sample_styles_dict) -> Path:
    """Create a temporary JSON file with sample styles."""
    file_path = tmp_path / 'styles.json'
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(sample_styles_dict, f, indent=2)
    return file_path


# ----------------------------------------------------------------------
# Tests for StyleSet
# ----------------------------------------------------------------------


def test_styleset_with_defaults():
    """Test that StyleSet provides default styles for missing levels."""
    # Create a StyleSet with only 'info' style
    info_style = InfoStyle({})
    style_set = StyleSet({'info': info_style})

    # Should return the provided style for 'info'
    assert style_set.get_style('info') is info_style
    # Should return a default style (InfoStyle with defaults) for missing levels
    debug_style = style_set.get_style('debug')
    assert isinstance(debug_style, DebugStyle)
    assert debug_style is not info_style


def test_styleset_merging():
    """Test that StyleSet merges provided styles with defaults."""
    custom_debug = DebugStyle({'level_color': 'magenta', 'show_icon': True})
    style_set = StyleSet({'debug': custom_debug})

    # 'debug' should be our custom one
    assert style_set.get_style('debug') is custom_debug
    # Others should be defaults
    assert isinstance(style_set.get_style('info'), InfoStyle)
    assert isinstance(style_set.get_style('warning'), WarningStyle)
    assert isinstance(style_set.get_style('error'), ErrorStyle)
    assert isinstance(style_set.get_style('critical'), CriticalStyle)


def test_styleset_case_insensitive():
    """Test that get_style works case-insensitively."""
    debug_style = DebugStyle({})
    style_set = StyleSet({'debug': debug_style})

    assert style_set.get_style('DEBUG') is debug_style
    assert style_set.get_style('Debug') is debug_style


# ----------------------------------------------------------------------
# Tests for InMemoryStyleRepository
# ----------------------------------------------------------------------


def test_in_memory_basic_loading(sample_styles_dict):
    """Test loading styles from an in-memory dictionary."""
    repo = InMemoryStyleRepository(sample_styles_dict)
    style_set = repo.load_styles()

    # Check that all expected levels are present
    assert isinstance(style_set.get_style('debug'), DebugStyle)
    assert isinstance(style_set.get_style('info'), InfoStyle)
    assert isinstance(style_set.get_style('warning'), WarningStyle)
    assert isinstance(style_set.get_style('error'), ErrorStyle)
    assert isinstance(style_set.get_style('critical'), CriticalStyle)


def test_in_memory_unknown_level_raises():
    """Test that providing an unknown level name raises UnknownStyleType."""
    bad_config = {
        'debug': {},
        'info': {},
        'unknown_level': {},  # this should cause an error
    }
    repo = InMemoryStyleRepository(bad_config)
    with pytest.raises(UnknownStyleType, match='Unknown level name: unknown_level'):
        repo.load_styles()


def test_in_memory_style_config_override(sample_styles_dict):
    """Test that style attributes are correctly set from config."""
    repo = InMemoryStyleRepository(sample_styles_dict)
    style_set = repo.load_styles()

    debug_style = style_set.get_style('debug')

    assert debug_style._show_icon is True
    assert debug_style._level_icon == '🐞'
    assert debug_style._level_color == 'cyan'
    assert debug_style._show_path is True
    assert debug_style._show_function is True
    assert debug_style._show_line is True

    info_style = style_set.get_style('info')
    assert info_style._level_color == 'green'
    assert info_style._msg_color == 'white'
    assert info_style._time_format == '%Y-%m-%d %H:%M:%S'


# ----------------------------------------------------------------------
# Tests for JsonStyleRepository
# ----------------------------------------------------------------------


def test_json_basic_loading(temp_styles_file, sample_styles_dict):
    """Test loading styles from a JSON file."""
    repo = JsonStyleRepository(temp_styles_file)
    style_set = repo.load_styles()

    # Same checks as in-memory
    assert isinstance(style_set.get_style('debug'), DebugStyle)
    assert isinstance(style_set.get_style('info'), InfoStyle)
    assert isinstance(style_set.get_style('warning'), WarningStyle)
    assert isinstance(style_set.get_style('error'), ErrorStyle)
    assert isinstance(style_set.get_style('critical'), CriticalStyle)


def test_json_missing_file(tmp_path):
    """Test that loading from a non-existent file raises StyleFileNotFoundError."""
    non_existent = tmp_path / 'no_such_file.json'
    repo = JsonStyleRepository(non_existent)
    with pytest.raises(StyleFileNotFoundError):
        repo.load_styles()


def test_json_invalid_json(tmp_path):
    """Test that invalid JSON raises StyleFormatError."""
    bad_file = tmp_path / 'bad.json'
    with open(bad_file, 'w') as f:
        f.write('{ this is not json }')
    repo = JsonStyleRepository(bad_file)
    with pytest.raises(StyleFormatError):
        repo.load_styles()


def test_json_unknown_level_raises(tmp_path):
    """Test that an unknown level in JSON raises UnknownStyleType."""
    bad_data = {
        'debug': {},
        'info': {},
        'unknown_level': {},
    }
    bad_file = tmp_path / 'bad.json'
    with open(bad_file, 'w') as f:
        json.dump(bad_data, f)
    repo = JsonStyleRepository(bad_file)
    with pytest.raises(UnknownStyleType, match='Unknown level name: unknown_level'):
        repo.load_styles()


# ----------------------------------------------------------------------
# Tests for LevelStyle properties (format fragments)
# ----------------------------------------------------------------------


def test_level_style_level_property():
    """Test that level property returns correct format fragment."""
    config = {
        'show_icon': True,
        'level_icon': '🔍',
        'show_level_str': True,
        'level_str': 'MYDEBUG',
        'level_color': 'blue',
    }
    style = DebugStyle(config)

    level_fragment = style.level
    # Should contain icon and level string, both colored
    assert '🔍' in level_fragment
    assert 'MYDEBUG' in level_fragment
    assert '<blue>' in level_fragment
    assert '</blue>' in level_fragment


def test_level_style_time_property():
    """Test that time property uses correct time format and color."""
    config = {
        'show_time': True,
        'time_format': '%d.%m.%Y %H:%M',
        'time_color': 'cyan',
    }
    style = InfoStyle(config)

    time_fragment = style.time
    assert '{time:%d.%m.%Y %H:%M}' in time_fragment
    assert '<cyan>' in time_fragment
    assert '</cyan>' in time_fragment


def test_level_style_msg_property():
    """Test that msg property includes color if configured."""
    config = {
        'show_msg': True,
        'msg_color': 'yellow',
    }
    style = WarningStyle(config)

    msg_fragment = style.msg
    assert '{message}' in msg_fragment
    assert '<yellow>' in msg_fragment
    assert '</yellow>' in msg_fragment


def test_level_style_empty_properties():
    """Test that properties return empty string when component is hidden."""
    config = {
        'show_path': False,
        'show_function': False,
        'show_line': False,
    }
    style = DebugStyle(config)

    assert style.path == ''
    assert style.function == ''
    assert style.line == ''


def test_level_style_get_format_string():
    """Test that get_format_string correctly replaces placeholders."""
    config = {
        'console_style': '[level] - msg (time)',
        'show_level_str': True,
        'level_str': 'INFO',
        'level_color': 'green',
        'show_msg': True,
        'msg_color': 'white',
        'show_time': True,
        'time_format': '%H:%M',
        'time_color': 'blue',
    }
    style = InfoStyle(config)
    format_string = style.get_format_string(handler_type='console')

    # Should replace 'level', 'msg', 'time' with their fragments
    assert '<green>INFO</green>' in format_string
    assert '<white>{message}</white>' in format_string
    assert '<blue>{time:%H:%M}</blue>' in format_string
    # The brackets and spaces should remain
    assert format_string.startswith('[')
    assert ' - ' in format_string
    assert ' (' in format_string and ')' in format_string
