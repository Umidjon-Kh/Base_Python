from .base import InfrastructureError


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
