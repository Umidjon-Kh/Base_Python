from typing import Dict, Any, Optional, List

# Project modules
from ...application.ports import RuleRepository
from ...domain.rules import Rule, RuleSet, ExtensionRule, SizeRule, CompositeRule
from ...domain.exceptions import RuleValidationError, UnknownRuleTypeError


class InMemoryRuleRepository(RuleRepository):
    """
    Builds a RuleSet from an in‑memory dictionary.
    Useful for CLI‑provided rules (--rules) and for combining with default rules.
    """

    __slots__ = ('rules_cfg', 'default_repo' 'combine')

    def __init__(
        self,
        rules_cfg: Dict[str, Any],
        default_repo: Optional[RuleRepository] = None,
        combine: bool = False,
    ):
        """
        Args:
            rules_cfg: Dictionary with the same structure as the JSON file.
            default_repo: Repository to load default rules from (if combine=True).
            combine: If True, merge default rules with the provided rules_cfg.
        """
        self.rules_cfg = rules_cfg
        self.default_repo = default_repo
        self.combine = combine

    def load_rules(self) -> RuleSet:
        if self.combine and self.default_repo:
            default_set = self.default_repo.load_rules()
            # Build user rules
            user_rules = self._build_rules_from_dict(self.rules_cfg)
            # Merge: user rules first (higher priority)
            combined_rules = user_rules + list(default_set.rules)
            # Other settings: user takes precedence
            other_behavior = self.rules_cfg.get('other_behavior', default_set.other_behavior)
            ignore_extensions = self.rules_cfg.get('ignore_extensions', default_set.ignore_extensions)
            ignore_size_more = self.rules_cfg.get('ignore_size_more_than', default_set.ignore_size_more_than)
            ignore_size_less = self.rules_cfg.get('ignore_size_less_than', default_set.ignore_size_less_than)
            merged_dict = {
                'rules': combined_rules,
                'other_behavior': other_behavior,
                'ignore_extensions': ignore_extensions,
                'ignore_size_more_than': ignore_size_more,
                'ignore_size_less_than': ignore_size_less,
            }
            return RuleSet(merged_dict)
        else:
            # Just build from given dict
            rules = self._build_rules_from_dict(self.rules_cfg)
            config = self.rules_cfg.copy()
            config['rules'] = rules
            return RuleSet(config)

    def _build_rules_from_dict(self, cfg: Dict[str, Any]) -> List[Rule]:
        rules_data = cfg.get('rules', [])
        if not isinstance(rules_data, list):
            raise RuleValidationError('\'rules\' must be a list')
        rules = []
        for item in rules_data:
            rules.append(self._parse_rule(item))
        return rules

    def _parse_rule(self, item: Dict[str, Any]) -> Rule:
        rule_type = item.get('type')
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
