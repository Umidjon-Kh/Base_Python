"""Organizer package Initializer"""

from .src import RuleManager, ConfigManager, OrganizerError, Organizer
from .logger import LogManager

__all__ = [
    'Organizer',
    'ConfigManager',
    'RuleManager',
    'LogManager',
    'OrganizerError',
]
__version__ = '0.2.0'
