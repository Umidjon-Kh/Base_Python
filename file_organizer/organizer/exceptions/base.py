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
