from typing import List, Optional

# Project modules
from ..entities import FileItem
from .rule import Rule


class CompositeRule(Rule):
    """
    Combines multiple rules with AND/OR logic.
    For AND: all sub‑rules must match; target segments are concatenated in order.
    For OR: the first matching sub‑rule determines the target segments.
    """

    def __init__(self, rules: List[Rule], operator: str = 'AND', priority: Optional[int] = 100):
        """
        Args:
            rules: List of Rule objects.
            operator: "AND" or "OR".
        """
        self.rules = rules
        self.operator = operator.upper()
        if self.operator not in ('AND', 'OR'):
            raise ValueError('CompositeRule operator must be \'AND\' or \'OR\'')
        self._priority = priority if priority is not None else 100

    @property
    def priority(self) -> int:
        return 100

    def match(self, file_item: FileItem) -> bool:
        if self.operator == 'AND':
            return all(rule.match(file_item) for rule in self.rules)
        else:  # OR
            return any(rule.match(file_item) for rule in self.rules)

    def target_segments(self, file_item: FileItem) -> List[str]:
        """
        For AND: collect segments from all sub‑rules (they all matched).
        For OR: find the first matching sub‑rule and return its segments.
        """
        if self.operator == 'AND':
            segments = []
            for rule in self.rules:
                # Since AND matched, every rule matched, so we can safely get segments
                segments.extend(rule.target_segments(file_item))
            return segments
        else:  # OR
            for rule in self.rules:
                if rule.match(file_item):
                    return rule.target_segments(file_item)
            # This point should never be reached because match() would have returned False
            return []
