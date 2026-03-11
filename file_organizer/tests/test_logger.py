"""
Tests for LoguruLogger adapter.
"""

import pytest
from pathlib import Path
from loguru import logger

from organizer.infrastructure.styles import StyleSet, DebugStyle, InfoStyle, WarningStyle, ErrorStyle, CriticalStyle
from organizer.infrastructure.logging import LoguruLogger
from organizer.exceptions import LogFileNotDefinedError


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def reset_loguru():
    """Remove all loguru handlers after each test to avoid interference."""
    yield
    logger.remove()


@pytest.fixture
def style_set() -> StyleSet:
    """Default StyleSet — all five levels with default styles."""
    return StyleSet({})


@pytest.fixture
def custom_style_set() -> StyleSet:
    """StyleSet with custom styles to verify they are applied."""
    return StyleSet(
        {
            'debug': DebugStyle({'show_icon': True, 'level_icon': '🐛', 'level_color': 'cyan'}),
            'info': InfoStyle({'level_color': 'green', 'msg_color': 'white'}),
            'warning': WarningStyle({'level_color': 'yellow'}),
            'error': ErrorStyle({'level_color': 'red', 'show_path': True}),
            'critical': CriticalStyle({'level_color': 'RED', 'show_line': True}),
        }
    )


@pytest.fixture
def console_config() -> dict:
    """Config with console-only logging at DEBUG level."""
    return {'console': {'enabled': True, 'level': 'DEBUG'}}


@pytest.fixture
def file_config(tmp_path) -> dict:
    """Config with both console (INFO) and file (DEBUG) logging."""
    return {
        'console': {'enabled': False, 'level': 'INFO'},
        'file': {
            'enabled': True,
            'level': 'DEBUG',
            'path': str(tmp_path / 'test.log'),
            'rotation': '1 MB',
            'retention': '1 day',
        },
    }


# ── Tests ─────────────────────────────────────────────────────────────────────


def test_console_all_levels_printed(style_set, console_config, capsys):
    """All five levels produce output when level is DEBUG."""
    log = LoguruLogger(console_config, style_set)
    log.debug('msg_debug')
    log.info('msg_info')
    log.warning('msg_warning')
    log.error('msg_error')
    log.critical('msg_critical')

    output = capsys.readouterr().err
    assert 'msg_debug' in output
    assert 'msg_info' in output
    assert 'msg_warning' in output
    assert 'msg_error' in output
    assert 'msg_critical' in output


def test_console_level_filtering(style_set, capsys):
    """Messages below the configured level are not printed."""
    config = {'console': {'enabled': True, 'level': 'WARNING'}}
    log = LoguruLogger(config, style_set)
    log.debug('hidden_debug')
    log.info('hidden_info')
    log.warning('visible_warning')

    output = capsys.readouterr().err
    assert 'hidden_debug' not in output
    assert 'hidden_info' not in output
    assert 'visible_warning' in output


def test_console_disabled_no_output(style_set, capsys):
    """No output when console is disabled."""
    config = {'console': {'enabled': False, 'level': 'DEBUG'}}
    log = LoguruLogger(config, style_set)
    log.info('should_not_appear')

    output = capsys.readouterr().err
    assert 'should_not_appear' not in output


def test_custom_styles_applied(custom_style_set, console_config, capsys):
    """Custom style with icon is reflected in the output."""
    log = LoguruLogger(console_config, custom_style_set)
    log.debug('styled_debug')

    output = capsys.readouterr().err
    assert '🐛' in output


def test_file_logging_writes_to_file(style_set, file_config):
    """Messages are written to the log file."""
    log_path = Path(file_config['file']['path'])
    log = LoguruLogger(file_config, style_set)

    log.debug('file_debug')
    log.info('file_info')
    log.warning('file_warning')

    logger.remove()  # flush

    assert log_path.exists()
    content = log_path.read_text()
    assert 'file_debug' in content
    assert 'file_info' in content
    assert 'file_warning' in content


def test_file_enabled_without_path_raises(style_set):
    """File logging enabled but path=None raises LogFileNotDefinedError."""
    config = {
        'console': {'enabled': False},
        'file': {'enabled': True, 'level': 'DEBUG', 'path': None},
    }
    with pytest.raises(LogFileNotDefinedError):
        LoguruLogger(config, style_set)


def test_rotation_and_retention_passed_to_loguru(style_set, tmp_path, mocker):
    """Rotation and retention values are forwarded to loguru.add."""
    config = {
        'console': {'enabled': False},
        'file': {
            'enabled': True,
            'level': 'DEBUG',
            'path': str(tmp_path / 'test.log'),
            'rotation': '1 day',
            'retention': '7 days',
        },
    }
    mock_add = mocker.patch('loguru.logger.add')
    LoguruLogger(config, style_set)

    file_calls = [c for c in mock_add.call_args_list if c[0][0] == config['file']['path']]
    assert len(file_calls) == 1
    _, kwargs = file_calls[0]
    assert kwargs['rotation'] == '1 day'
    assert kwargs['retention'] == '7 days'
