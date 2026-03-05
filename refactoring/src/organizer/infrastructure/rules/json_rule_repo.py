from json import JSONDecodeError, load as loader
from pathlib import Path
from typing import Dict, Any

from application.ports.rule_repository import RuleRepository
from domain.rules.rule import Rule, ExtensionRule
from domain.rules.rule_set import RuleSet
from domain.exceptions import (
    RuleFileNotFoundError,
    RuleFormatError,
    RuleValidationError,
    UnknownRuleTypeError,
)


class JsonRuleRepository(RuleRepository):
    """
    Loads rules from a JSON file.
    Expected format: list of objects with fields:
        - type: string (currently only "extension")
        - extensions: list of strings (extensions, may include dot)
        - folder: string
    """
    def __init__(self, file_path: Path):
        self.file_path = file_path

    def load_rules(self) -> RuleSet:
        if not self.file_path.exists():
            raise RuleFileNotFoundError(f'Rules file not found: {self.file_path}')

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = loader(f)
        except JSONDecodeError as exc:
            raise RuleFormatError(f'Invalid JSON in rules file: {exc}')
        except IOError as exc:
            raise RuleFileNotFoundError(f'Cannot read rules file: {exc}')

        if not isinstance(data, dict):
            raise RuleFormatError('Rules file must contain a dictionary with \'rules\' list and optional settings')

        # Extract global settings
        other_behavior = data.get('other_behavior', 'use_other')
        ignore_extensions = data.get('ignore_extensions', [])

        # Extract rules list
        rules_data = data.get('rules', [])
        if not isinstance(rules_data, list):
            raise RuleFormatError('\'rules\' must be a list')

        rules = []
        for item in rules_data:
            rule = self._parse_rule(item)
            rules.append(rule)

        return RuleSet(rules, other_behavior, ignore_extensions)

    def _parse_rule(self, item: Dict[str, Any]) -> Rule:
        rule_type = item.get('type')
        if rule_type == 'extension':
            extensions = item.get('extensions')
            folder = item.get('folder')
            if not extensions or not folder:
                raise RuleValidationError(f'Extension rule missing \'extensions\' or \'folder\': {item}')
            if not isinstance(extensions, list):
                raise RuleValidationError(f'\'extensions\' must be a list: {item}')
            # Normalizing rules
            normalized = []
            for ext in extensions:
                if not isinstance(ext, str):
                    raise RuleValidationError(f'Extension must be a string: {ext}')
                ext = ext.lower()
                if not ext.startswith('.'):
                    ext = '.' + ext
                normalized.append(ext)
            return ExtensionRule(normalized, folder)
        else:
            raise UnknownRuleTypeError(f'Unknown rule type: {rule_type}')
