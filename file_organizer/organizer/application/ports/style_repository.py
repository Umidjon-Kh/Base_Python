from abc import ABC, abstractmethod

# Project modules
from ...domain.styles import StyleSet


class StyleRepository(ABC):
    """
    Abstract interface for loading styles.
    Any concrete adapter (JSON, in-memory, etc.) must implement this.
    """

    @abstractmethod
    def load_styles(self) -> StyleSet:
        """
        Load and return a StyleSet containing all level styles.

        Returns:
            A fully configured StyleSet.

        Raises:
            StyleError subclasses (StyleFileNotFoundError, StyleFormatError, etc.)
            in case of failure.
        """
        pass
