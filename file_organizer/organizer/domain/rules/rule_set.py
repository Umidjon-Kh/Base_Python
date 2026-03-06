from typing import Optional, Any, Dict

# Project modules
from ..entities import FileItem
from ..exceptions import RuleNotFoundError, UnknownBehaviorType


class RuleSet:
    """
    Container for all rules, plus global settings about how to handle unmapped files.
    This class encapsulates the logic of applying rules to a file item.
    It does not know anything about JSON or external sources – pure business logic.
    """

    __slots__ = ('rules', 'other_behavior', 'ignore_extensions', 'ignore_size_more_than', 'ignore_size_less_than')

    def __init__(self, rules_cfg: Dict[str, Any]):
        """
        Rules Cfg Args:
            rules: List of Rule objects, Sorted by priority level.
            other_behavior: What to do when no rule matches.
                - "use_other": return folder "Other"
                - "raise": raise RuleNotFoundError
                - "ignore": return None (file will be skipped)
            ignore_extensions: List of extensions to always ignore (skipped even if a rule matches)
            ignore_size_more_than: Ignore file that size more than (skipped even if rule matches)
            ignore_size_less_than: Ignore file that size less than (skipped even if rule matches).
        """
        self.rules = sorted(rules_cfg.pop('rules'), key=lambda r: r.priority, reverse=True)
        self.other_behavior = rules_cfg.pop('other_behavior')
        self.ignore_extensions = [
            ext.lower() if ext.startswith('.') else f'.{ext.lower()}'
            for ext in (rules_cfg.pop('ignore_extensions') or [])
        ]
        # Checking ignore size values before value assigment
        more = rules_cfg.pop('ignore_size_more_than')
        less = rules_cfg.pop('ignore_size_less_than')
        if less is not None and less <= 0:
            raise ValueError('ignore_size_less_than must be > 0')
        if more is not None and more <= 0:
            raise ValueError('ignore_size_more_than must be > 0')
        if less is not None and more is not None and less >= more:
            raise ValueError('ignore_size_less_than must be less than ignore_size_more_than')
        # Assigment values
        self.ignore_size_more_than = more
        self.ignore_size_less_than = less

    def get_target_folder(self, file_item: FileItem) -> Optional[str]:
        """
        Determine the target folder for a file item.

        Returns:
            - folder name if a rule matches and file is not ignored
            - None if the file should be ignored (by extension, size or other_behavior = "ignore")
            - raises RuleNotFoundError if other_behavior == "raise" and no rule matches
        """
        # 1. Check ignore by extension
        if file_item.suffix.lower() in self.ignore_extensions:
            return None

        # 2. Check ignore by size if its not None
        if file_item.size is not None:
            if self.ignore_size_more_than is not None and file_item.size >= self.ignore_size_more_than:
                return None
            if self.ignore_size_less_than is not None and file_item.size <= self.ignore_size_less_than:
                return None

        # 2. Find a matching rule
        for rule in self.rules:
            if rule.match(file_item):
                segments = rule.target_segments(file_item)
                return '/'.join(segments)

        # 3. No rule matched – handle according to other_behavior
        if self.other_behavior == 'use_other':
            return 'Other'
        elif self.other_behavior == 'raise':
            raise RuleNotFoundError(f'No rule found for file: {file_item.name}')
        elif self.other_behavior == 'ignore':
            return None
        else:
            raise UnknownBehaviorType(f'Unknown behavior type: {self.other_behavior}')
