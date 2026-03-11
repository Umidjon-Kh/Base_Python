from typing import Dict, Any, Optional, List

# Project modules
from ...application.ports import RuleRepository
from ...domain.rules import Rule, RuleSet, ExtensionRule, SizeRule, CompositeRule
from ...exceptions import RuleValidationError, UnknownRuleTypeError


class InMemoryRuleRepository(RuleRepository):
    """
    Builds a RuleSet from an in‑memory dictionary.
    Useful for CLI‑provided rules (--rules) and for combining with default rules.
    """

    __slots__ = ('_rules_cfg', '_rules_repo', '_default_repo', '_combine')

    def __init__(
        self,
        default_repo: RuleRepository,
        rules_cfg: Optional[Dict[str, Any]] = None,
        rules_repo: Optional[RuleRepository] = None,
        combine: bool = False,
    ) -> None:
        """
        Args:
            rules_cfg: Dictionary with the same structure as the JSON file.
            default_repo: Repository to load default rules from (if combine=True).
            combine: If True, merge default rules with the provided rules_cfg.
        """
        self._default_repo = default_repo
        self._rules_repo = rules_repo
        self._combine = combine
        self._rules_cfg = rules_cfg

    def load_rules(self) -> RuleSet:
        """
        Main code for loading and combining setter params if user cfg is not None
        Priority of setter attributes
            3 - default rules repository
            2 - custom user rules repository
            1 - custom user config args
        Returns RuleSetter with all combined rules
        """
        # List of rules: extension, size, composite, ...
        rules_data = []
        # Setting default setter
        setter = self._default_repo.load_rules()
        # If combine overrides all default setter attributes with user args
        if self._combine:
            rules_data = setter.rules
            # Adding rules from custom fules repository
            if self._rules_repo is not None:
                user_rule_set = self._rules_repo.load_rules()
                rules_data = user_rule_set.rules + rules_data
                setter = user_rule_set
            # Adding user custom rules if its not None
            if self._rules_cfg is not None:
                user_rules = self._build_rules_from_dict(self._rules_cfg.get('rules', []))
                rules_data = user_rules + rules_data
        # Otherwise if combine is false only using user rules
        # But if user custom rules cfg and custom rules repo is None
        # Using default rules attributes, without rules list
        else:
            if self._rules_repo is not None:
                user_rule_set = self._rules_repo.load_rules()
                rules_data = user_rule_set.rules
                setter = user_rule_set
            if self._rules_cfg is not None:
                user_rules = self._build_rules_from_dict(self._rules_cfg.get('rules', []))
                rules_data = user_rules + rules_data

        # Building new config from setter and user config params
        config = self._config_builder(self._rules_cfg or {}, rules_data, setter)
        # Returning RuleSet
        return RuleSet(config)

    def _config_builder(
        self,
        config: Dict[str, Any],
        rules: List[Rule],
        setter: RuleSet,
    ) -> Dict[str, Any]:
        """Returns updated config with setter and user rule setter config params"""
        builded_config = {
            'other_behavior': config.get('other_behavior', setter.other_behavior),
            'ignore_extensions': config.get('ignore_extensions', setter.ignore_extensions),
            'ignore_size_more_than': config.get('ignore_size_more_than', setter.ignore_size_more_than),
            'ignore_size_less_than': config.get('ignore_size_less_than', setter.ignore_size_less_than),
            'rules': rules,
        }
        return builded_config

    def _build_rules_from_dict(self, rules_data: list) -> List[Rule]:
        if not isinstance(rules_data, list):
            raise RuleValidationError('\'rules\' must be a list')
        rules = []
        for item in rules_data:
            rules.append(self._parse_rule(item))
        return rules

    def _parse_rule(self, item: Dict[str, Any]) -> Rule:
        rule_type = item.get('type', None)
        priority = item.get('priority', None)
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
