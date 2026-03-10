"""
Tests for LoguruLogger adapter.
"""

import pytest
import sys
from pathlib import Path
from loguru import logger

from organizer.infrastructure.styles import StyleSet, DebugStyle, InfoStyle, WarningStyle, ErrorStyle, CriticalStyle
from organizer.infrastructure.logging import LoguruLogger


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_loguru():
    """Remove all handlers after each test to avoid interference."""
    yield
    logger.remove()


@pytest.fixture
def style_set() -> StyleSet:
    """Create a StyleSet with default styles."""
    return StyleSet({})  # empty dict -> all defaults


@pytest.fixture
def sample_styles() -> StyleSet:
    """Create a StyleSet with some custom styles for testing."""
    custom_styles = {
        'debug': DebugStyle(
            {
                'show_icon': True,
                'level_icon': '🐛',
                'level_color': 'cyan',
                'show_path': True,
                'show_function': True,
                'show_line': True,
            }
        ),
        'info': InfoStyle(
            {
                'level_color': 'green',
                'msg_color': 'white',
                'time_format': '%H:%M:%S',
            }
        ),
        'warning': WarningStyle(
            {
                'level_color': 'yellow',
                'msg_color': 'yellow',
            }
        ),
        'error': ErrorStyle(
            {
                'level_color': 'red',
                'msg_color': 'red',
                'show_path': True,
            }
        ),
        'critical': CriticalStyle(
            {
                'level_color': 'RED',
                'msg_color': 'RED',
                'show_line': True,
            }
        ),
    }
    return StyleSet(custom_styles)


@pytest.fixture
def console_config() -> dict:
    """Configuration for console-only logging."""
    return {'console': {'enabled': True, 'level': 'DEBUG'}}


@pytest.fixture
def file_config(tmp_path) -> dict:
    """Configuration for file logging."""
    log_file = tmp_path / 'test.log'
    return {
        'console': {'console_level': 'INFO'},
        'file': {
            'enabled': True,
            'level': 'DEBUG',
            'path': str(log_file),
            'rotation': '1 MB',
            'retention': '1 day',
        },
    }


# ----------------------------------------------------------------------
# Helper to capture stderr output
# ----------------------------------------------------------------------


@pytest.fixture
def capture_stderr(capsys):
    """Capture stderr output and return as string."""

    def _capture():
        captured = capsys.readouterr()
        return captured.err

    return _capture


# ----------------------------------------------------------------------
# Tests for LoguruLogger
# ----------------------------------------------------------------------


def test_logger_console_output(style_set, console_config, capture_stderr):
    """Test that log messages are printed to stderr with correct formatting."""
    log = LoguruLogger(console_config, style_set)

    log.debug('Debug message')
    log.info('Info message')
    log.warning('Warning message')
    log.error('Error message')
    log.critical('Critical message')

    output = capture_stderr()
    lines = output.strip().split('\n')

    # Should have 5 lines
    assert len(lines) == 5

    # Check that each level appears (exact format depends on defaults)
    assert any('DEBUG' in line and 'Debug message' in line for line in lines)
    assert any('INFO' in line and 'Info message' in line for line in lines)
    assert any('WARNING' in line and 'Warning message' in line for line in lines)
    assert any('ERROR' in line and 'Error message' in line for line in lines)
    assert any('CRITICAL' in line and 'Critical message' in line for line in lines)


def test_logger_level_filtering(style_set, console_config, capture_stderr):
    """Test that messages below console_level are not printed."""
    config = console_config.copy()
    config['console']['level'] = 'WARNING'  # only WARNING and above
    log = LoguruLogger(config, style_set)

    log.debug('Debug message')
    log.info('Info message')
    log.warning('Warning message')
    log.error('Error message')
    log.critical('Critical message')

    output = capture_stderr()
    lines = output.strip().split('\n')

    # Only WARNING, ERROR, CRITICAL should appear
    assert len(lines) == 3
    assert 'Debug message' not in output
    assert 'Info message' not in output
    assert 'Warning message' in output
    assert 'Error message' in output
    assert 'Critical message' in output


def test_logger_custom_styles(sample_styles, console_config, capture_stderr):
    """Test that custom styles are applied to log messages (icons and level names)."""
    log = LoguruLogger(console_config, sample_styles)

    log.debug('Debug message')
    log.info('Info message')
    log.warning('Warning message')
    log.error('Error message')
    log.critical('Critical message')

    output = capture_stderr()

    # Check that debug icon appears
    assert '🐛' in output

    # Check that all level names appear
    assert 'DEBUG' in output
    assert 'INFO' in output
    assert 'WARNING' in output
    assert 'ERROR' in output
    assert 'CRITICAL' in output


def test_logger_file_output(tmp_path, style_set, file_config, capture_stderr):
    """Test that log messages are written to a file when file_path is provided."""
    log_file = Path(file_config['file']['path'])
    log = LoguruLogger(file_config, style_set)

    log.debug('Debug file message')
    log.info('Info file message')
    log.warning('Warning file message')

    # Also check that console still prints according to console_level (INFO)
    console_output = capture_stderr()
    assert 'Debug file message' not in console_output  # below console level
    assert 'Info file message' in console_output
    assert 'Warning file message' in console_output

    # Now read the log file
    assert log_file.exists()
    with open(log_file, 'r') as f:
        file_content = f.read()

    # File should have all messages (file_level = DEBUG)
    assert 'Debug file message' in file_content
    assert 'Info file message' in file_content
    assert 'Warning file message' in file_content


def test_logger_rotation_and_retention_passed(tmp_path, style_set, mocker):
    """Test that rotation and retention parameters are passed to loguru.add."""
    config = {
        'console': {
            'level': 'INFO',
        },
        'file': {
            'enabled': True,
            'level': 'DEBUG',
            'path': str(tmp_path / 'test.log'),
            'rotation': '1 day',
            'retention': '7 days',
        },
    }

    # Mock loguru.add to capture arguments
    mock_add = mocker.patch('loguru.logger.add')

    LoguruLogger(config, style_set)

    # Should be called twice: once for console, once for file
    assert mock_add.call_count == 2

    # Find the file handler call
    file_calls = [call for call in mock_add.call_args_list if call[0][0] == config['file']['path']]
    assert len(file_calls) == 1
    call_args, call_kwargs = file_calls[0]
    assert call_kwargs['rotation'] == '1 day'
    assert call_kwargs['retention'] == '7 days'


def test_logger_no_file_if_path_missing(style_set, console_config, mocker):
    """Test that file handler is not added if file_path is missing."""
    mock_add = mocker.patch('loguru.logger.add')

    LoguruLogger(console_config, style_set)

    # Should be called only once (console)
    assert mock_add.call_count == 1
    # The call should be for stderr
    call_args, call_kwargs = mock_add.call_args
    assert call_args[0] == sys.stderr
