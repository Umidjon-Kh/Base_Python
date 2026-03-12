from abc import ABC, abstractmethod
from typing import Any


class Logger(ABC):
    """
    Abstract interface for logging.
    Any concrete logger adapter must implement this.
    """

    @abstractmethod
    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a debug message."""
        pass

    @abstractmethod
    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an info message."""
        pass

    @abstractmethod
    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a warning message."""
        pass

    @abstractmethod
    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an error message."""
        pass

    @abstractmethod
    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a critical message."""
        pass
