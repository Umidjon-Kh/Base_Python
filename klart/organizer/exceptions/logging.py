from .base import InfrastructureError


# ----- Logging errors (optional) -----
class LoggingError(InfrastructureError):
    """Base class for logging configuration errors."""

    pass


class LogFileNotDefinedError(LoggingError):
    """Raises when file logging enabled but file_path is not defined"""

    pass
