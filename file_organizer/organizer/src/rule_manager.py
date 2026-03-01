import json
from pathlib import Path
from typing import Dict, Optional
from .exceptions import RuleError

# class to configure rules of organizer
class RuleManager:
    """
    Manages with rules of sort: ext -> folder
    Auto adds User Custom rules from cli and rules file path
    to Rules, User Rules always Priority higher than default rules
    """