import json
from pathlib import Path
from typing import Dict, Optional
from ..exceptions import PathError, RuleError


# Class to load rules for rule_manager
class RuleLoader:
    """Loader to load rules for RuleManager"""

    # default rules path for rule_manager
    DEFAULT_RULES_FILE = Path(__file__).parent.parent.parent / 'configs' / 'default_rules.json'

    __slots__ = ('default_rules_file', '_rules_cache')

    def __init__(self, default_rules_path: Optional[str] = None) -> None:
        if default_rules_path and (p := Path(default_rules_path).resolve()).exists():
            self.default_rules_file = p
        else:
            self.default_rules_file = self.DEFAULT_RULES_FILE
        self._rules_cache: Dict = {}

    def load_rules(self, custom_path: Optional[str] = None) -> Dict:
        """Loads rules from file (Custom or Defaults)"""
        # Checking custom path is not None and exists or not
        if custom_path and (p := Path(custom_path).resolve()).exists():
            path = p
        else:
            path = self.default_rules_file
        # If we cached rules we return it
        if self._rules_cache:
            return self._rules_cache
        try:
            with open(path, encoding='utf-8') as file:
                self._rules_cache = json.load(file)
            # Chacking rules in right type or not
            if not isinstance(self._rules_cache, dict):
                raise RuleError('File of rules must contain dict')
            return self._rules_cache
        except (IOError, json.JSONDecodeError) as exc:
            raise PathError(f'Failed to load rules: {exc}')
