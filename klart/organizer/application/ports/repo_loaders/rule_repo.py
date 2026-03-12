from abc import ABC, abstractmethod

# Project modules
from ....domain import RuleSet


class RuleRepository(ABC):
    """
    Port for loading sorting rules.
    Any concrete implementation must return a fully configured RuleSet.
    """

    @abstractmethod
    def load_rules(self) -> RuleSet:
        """
        Load and return a RuleSet containing all rules and settings.
        May raise RuleError subclasses in case of failure.
        """
        pass
