# domain/rules/rule_set.py
from typing import List, Optional
from domain.entities import FileItem

# Project modules
from .rule import Rule
from ..exceptions import RuleNotFoundError


class RuleSet:
    """
    Container for all rules, plus global settings about how to handle unmapped files.
    """

    def __init__(
        self, rules: List[Rule], other_behavior: str = 'use_other', ignore_extensions: Optional[List[str]] = None
    ):
        self.rules = rules
        self.other_behavior = other_behavior  # "use_other", "raise", "ignore"
        self.ignore_extensions = [ext.lower() for ext in (ignore_extensions or [])]

    def get_target_folder(self, file_item: FileItem) -> Optional[str]:
        """
        Determine the target folder for a file item.
        Returns:
            - folder name if a rule matches
            - None if the file should be ignored (skip)
            - raises RuleNotFoundError if other_behavior == "raise" and no rule matches
        """
        # 1. Check if file should be ignored (by extension)
        if file_item.suffix.lower() in self.ignore_extensions:
            return None  # skip this file

        # 2. Try to find a matching rule
        for rule in self.rules:
            if rule.match(file_item):
                return rule.target_folder()

        # 3. No rule matched – handle according to other_behavior
        if self.other_behavior == 'use_other':
            return 'Other'
        elif self.other_behavior == 'raise':
            raise RuleNotFoundError(f'No rule found for file: {file_item.name}')
        elif self.other_behavior == 'ignore':
            return None
        else:
            # fallback (should not happen)
            return 'Other'
