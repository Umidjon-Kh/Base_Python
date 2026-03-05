from abc import ABC, abstractmethod

# Project modules
from domain.rules.rule_set import RuleSet


class RuleRepository(ABC):
    """
    Port for loading sorting rules from some source (file, db, etc.).
    """

    @abstractmethod
    def load_rules(self) -> RuleSet:
        """Load all rules and return them as a list of Rule objects."""
        pass
