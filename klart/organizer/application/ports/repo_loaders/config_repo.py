from abc import ABC, abstractmethod

# Project module: App Config
from ..config import AppConfig


class ConfigRepository(ABC):
    """
    Port for loading application configuration.

    Any concrete adapter (JSON, in-memory, environment variables, etc.)
    must implement this interface.
    """

    @abstractmethod
    def load_config(self) -> AppConfig:
        """
        Load and return the application configuration.

        Returns:
            A fully populated AppConfig instance.

        Raises:
            ConfigError subclasses: ConfigNotFoundError, ConfigFormatError,
                                     ConfigValidationError in case of failure.
        """
        pass
