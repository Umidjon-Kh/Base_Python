from .base import InfrastructureError


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
