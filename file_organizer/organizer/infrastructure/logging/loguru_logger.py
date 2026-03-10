import sys
from typing import Dict, Any
from loguru import logger

# Project modules
from ...application.ports import Logger as LoggerPort
from ..styles.level_style import StyleSet
from ...exceptions import LogFileNotDefinedError


class LoguruLogger(LoggerPort):
    """
    Adapter for loguru logger.
    Configures loguru based on provided settings and styles.
    """

    def __init__(self, config: Dict[str, Any], style_set: StyleSet) -> None:
        """
        Args:
            config: Dictionary with logging configuration.
                Expected keys:
                    - console_level: str (e.g., "INFO")
                    - file_level: str (e.g., "DEBUG")
                    - file_path: Optional[str] (path to log file)
                    - rotation: Optional[str] (log rotation, e.g., "1 day")
                    - retention: Optional[str] (log retention, e.g., "7 days")
            style_set: StyleSet containing styles for all levels.
        """
        self._config = config
        self._style_set = style_set
        self._configure()

    def _configure(self) -> None:
        """Configure loguru handlers based on config."""
        # Remove default handler
        logger.remove()

        # Console handler
        console_cfg = self._config.get('console', {})
        if console_cfg.get('enabled', True):
            console_level = console_cfg.get('console_level', 'INFO').upper()
            logger.add(
                sys.stderr,
                level=console_level,
                format=self._make_formatter('console'),
            )

        # File handler if file_path is provided
        file_cfg = self._config.get('file', {})
        if file_cfg.get('enabled', False):
            file_path = file_cfg.get('file_path', None)
            if file_path is not None:
                file_level = file_cfg.get('file_level', 'DEBUG').upper()
                rotation = file_cfg.get('rotation', '1 day')
                retention = file_cfg.get('retention', '7 days')
                logger.add(
                    file_path,
                    level=file_level,
                    format=self._make_formatter('file'),
                    rotation=rotation,
                    retention=retention,
                )
            else:
                raise LogFileNotDefinedError('Log file path is not defined')

    def _make_formatter(self, handler_type: str):
        """
        Create a formatter function for loguru.
        The function retrieves the appropriate style for the record's level
        and returns the format string.
        """

        def formatter(record):
            level_name = record['level'].name
            style = self._style_set.get_style(level_name)
            return style.get_format_string(handler_type) + '\n'

        return formatter

    # Implement LoggerPort methods
    def debug(self, message: str, *args, **kwargs):
        logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        logger.critical(message, *args, **kwargs)
