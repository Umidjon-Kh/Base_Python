"""Logger for organizer to stream and write all logs"""

from .standard import standard_logger
from .loguru_log import loguru_logger

__all__ = ['standard_logger', 'loguru_logger']
