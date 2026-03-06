import json
from pathlib import Path
from typing import Dict, Any, Union

# Project modules
from application.ports import RuleRepository
from domain.rules import Rule, ExtensionRule, SizeRule, CompositeRule, RuleSet
from domain.exceptions import (
    RuleFileNotFoundError,
    RuleFormatError,
    RuleValidationError,
    UnknownRuleTypeError,
)


class JsonRuleRepository(RuleRepository):
    """
    Loads rules from a JSON file.
    Expected format: dictionary with keys:
        - other_behavior
        - ignore_extensions (list)
        - ignore_size_more_than (int or null)
        - ignore_size_less_than (int or null)
        - rules: list of rule objects
    Each rule object may contain a "priority" field; if missing, a default priority is assigned.
    """

    __slots__ = ('file_path')

    def __init__(self, file_path: Union[Path, str]):
        self.file_path = file_path if isinstance(file_path, Path) else Path(file_path)

    def load_rules(self) -> RuleSet:
        if not self.file_path.exists():
            raise RuleFileNotFoundError(f'Rules file not found: {self.file_path}')

        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except (IOError, json.JSONDecodeError) as exc:
            raise RuleFormatError(f'Invalid JSON in rules file: {exc}')

        if not isinstance(data, dict):
            raise RuleFormatError('Rules file must contain a dictionary')

        # Extract global settings and rules list
        other_behavior = data.get('other_behavior', 'use_other')
        ignore_extensions = data.get('ignore_extensions', [])
        ignore_size_more = data.get('ignore_size_more_than', None)
        ignore_size_less = data.get('ignore_size_less_than', None)
        rules_data = data.get('rules', [])
        if not isinstance(rules_data, list):
            raise RuleFormatError('\'rules\' must be a list')

        # Build rule objects
        rules = []
        for item in rules_data:
            rule = self._parse_rule(item)
            rules.append(rule)

        # Create the config dictionary for RuleSet
        config = {
            'rules': rules,
            'other_behavior': other_behavior,
            'ignore_extensions': ignore_extensions,
            'ignore_size_more_than': ignore_size_more,
            'ignore_size_less_than': ignore_size_less,
        }
        return RuleSet(config)

    def _parse_rule(self, item: Dict[str, Any]) -> Rule:
        rule_type = item.get('type')
        priority = item.get('priority')
        # If priority not provided, default will be set inside each rule's constructor
        if rule_type == 'extension':
            extensions = item.get('extensions')
            folder = item.get('folder')
            if not extensions or not folder:
                raise RuleValidationError(f'Extension rule missing \'extensions\' or \'folder\': {item}')
            return ExtensionRule(extensions, folder, priority)
        elif rule_type == 'size':
            min_size = item.get('min', None)
            max_size = item.get('max', None)
            folder = item.get('folder', None)
            if folder is None:
                raise RuleValidationError(f'Size rule missing \'folder\' attribute: {item}')
            if min_size is None and max_size is None:
                raise RuleValidationError('Size rule must have \'min\' or \'max\'')
            return SizeRule(min_size, max_size, folder, priority)
        elif rule_type == 'composite':
            operator = item.get('operator', 'AND')
            sub_rules_data = item.get('rules')
            if not isinstance(sub_rules_data, list):
                raise RuleValidationError('Composite rule must have a \'rules\' list')
            sub_rules = [self._parse_rule(sub) for sub in sub_rules_data]
            return CompositeRule(sub_rules, operator, priority)
        else:
            raise UnknownRuleTypeError(f'Unknown rule type: {rule_type}')
