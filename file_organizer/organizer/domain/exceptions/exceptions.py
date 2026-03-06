"""
Centralized exceptions for the entire organizer application.
All custom exceptions inherit from OrganizerError.
"""


class OrganizerError(Exception):
    """Base exception for all organizer errors."""

    pass


# ----------------------------------------------------------------------
# Domain exceptions (related to entities and business rules)
# ----------------------------------------------------------------------


class DomainError(OrganizerError):
    """Base class for domain-related errors."""

    pass


class InvalidPathError(DomainError):
    """Raised when a path is invalid (doesn't exist, wrong type, etc.)."""

    pass


class DuplicateChildError(DomainError):
    """Raised when trying to add a duplicate child to a Directory."""

    pass


# ----------------------------------------------------------------------
# Application exceptions (use cases, DTOs, etc.)
# ----------------------------------------------------------------------


class ApplicationError(OrganizerError):
    """Base class for application-layer errors."""

    pass


class OrganizeRequestError(ApplicationError):
    """Raised when the organize request DTO is invalid."""

    pass


# ----------------------------------------------------------------------
# Infrastructure exceptions (file system, config, rules, logging)
# ----------------------------------------------------------------------


class InfrastructureError(OrganizerError):
    """Base class for infrastructure-layer errors."""

    pass


# ----- File system errors -----
class FileSystemError(InfrastructureError):
    """Base class for file system operation errors."""

    pass


class SourceFileNotFoundError(FileSystemError):
    """Raised when a file or directory does not exist."""

    pass


class PermissionDeniedError(FileSystemError):
    """Raised when lacking permissions to read/write a file or directory."""

    pass


class DestinationExistsError(FileSystemError):
    """Raised when a destination path already exists and cannot be overwritten."""

    pass


# ----- Configuration errors -----
class ConfigError(InfrastructureError):
    """Base class for configuration loading/parsing errors."""

    pass


class ConfigNotFoundError(ConfigError):
    """Raised when a configuration file is not found."""

    pass


class ConfigFormatError(ConfigError):
    """Raised when a configuration file has invalid format (e.g., not a dict)."""

    pass


class ConfigValidationError(ConfigError):
    """Raised when a configuration value fails validation (e.g., wrong type)."""

    pass


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


# ----- Logging errors (optional) -----
class LoggingError(InfrastructureError):
    """Base class for logging configuration errors."""

    pass
