from abc import ABC, abstractmethod
from typing import Optional


class StyleRepository(ABC):
    """
    Port for loading log styling configurations.
    Styles define how log messages are formatted (colors, layout, etc.).
    """

    @abstractmethod
    def get_console_format(self, style_name: str) -> Optional[str]:
        """
        Return the format string for the given console style name.
        Return None if the style is not found.
        """
        pass

    @abstractmethod
    def get_file_format(self, style_name: str) -> Optional[str]:
        """
        Return the format string for the given file style name.
        Return None if the style is not found.
        """
        pass
