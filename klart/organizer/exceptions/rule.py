from .base import InfrastructureError


# ----- Rule errors -----
class RuleError(InfrastructureError):
    """Base class for rule loading/parsing errors."""

    pass


class RuleFileNotFoundError(RuleError):
    """Raised when a rules file is not found."""

    pass


class RuleFormatError(RuleError):
    """Raised when a rules file has invalid format (e.g., not a list)."""

    pass


class UnknownRuleTypeError(RuleError):
    """Raised when a rule has an unknown type (e.g., 'size' not implemented)."""

    pass


class RuleValidationError(RuleError):
    """Raised when a rule definition is missing required fields or has invalid values."""

    pass


class RuleNotFoundError(RuleError):
    """Raised when a rule is not found (e.g., '.sh' not in rules)"""

    pass


class UnknownBehaviorType(RuleError):
    """Raised when a other behavior type is unknown"""

    pass
