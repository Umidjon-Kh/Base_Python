from abc import ABC, abstractmethod
from typing import List

# Project modules
from domain.entities import FileItem


class Rule(ABC):
    """
    Base class for all sorting rules.
    Each rule decides whether a file matches and returns the target folder name.
    """

    @abstractmethod
    def match(self, file_item: FileItem) -> bool:
        """Check if the file matches this rule."""
        pass

    @abstractmethod
    def target_folder(self) -> str:
        """Return the folder name where matching files should go."""
        pass


class ExtensionRule(Rule):
    """
    Default rule: Extension Rule
    Rule that matches files by their extension.
    """

    def __init__(self, extensions: List[str], folder: str):
        self.extensions = extensions
        self.folder = folder

    def match(self, file_item: FileItem) -> bool:
        return file_item.suffix.lower() in self.extensions

    def target_folder(self) -> str:
        return self.folder
