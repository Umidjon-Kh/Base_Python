from abc import ABC, abstractmethod
from typing import Dict, Any


class StyleRepository(ABC):
    """
    Port for loading log styling configurations.
    Styles define how log messages are formatted (colors, layout, etc.).
    The repository returns a dictionary containing all styles, typically with keys
    'console' and 'file', each mapping style names to format strings.
    """

    @abstractmethod
    def load_styles(self) -> Dict[str, Any]:
        """
        Load all styles and return them as a dictionary.
        The exact structure depends on the implementation, but it should contain
        at least the keys 'console' and 'file', each being a dictionary of style names to format strings.
        Raises StyleError subclasses in case of failure.
        """
        pass
