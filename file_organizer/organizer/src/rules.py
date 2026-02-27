import json
from pathlib import Path
from typing import Dict, Optional
from . import RuleError


class RuleManager:
    """Manages with rules of sort: ext -> folder"""

    # Slots for instance
    __slots__ = ('__rules',)

    DEFAULT_RULES_FILE = Path(__file__).parent.parent / 'configs' / 'default_rules.json'

    # Initializing rules and rules file
    def __init__(
        self, rules: Optional[Dict[str, str]] = None, rules_file: Optional[Path] = None, combine: bool = False
    ) -> None:
        """
        :param rules: Dict of rules in format {'.ext': 'folder'}
        :param rules_file: Path to JSON-file with rules
        """

        self.__rules = {}
        # 1.Action: combines default and user rules
        if combine:
            self.load_defaults()
        # 2.Action: Loading rules from file
        if rules_file:
            self.load_from_file(rules_file)
        # 3.Action: Adding user rules to attr
        if rules:
            # Normalizing rules
            normalized = self.normalize_dict(rules)
            self.__rules.update(normalized)
        # 4.Action: Setting default rules
        if not self.__rules:
            self.load_defaults()

    # Getter for private attr
    @property
    def rules(self) -> Dict:
        """Retruns copy of rules"""
        return self.__rules.copy()

    # Normalizing rules in dict
    @staticmethod
    def normalize_dict(data: Dict[str, str]) -> Dict[str, str]:
        """Returns fight format of dict of rules"""
        normalized = {}
        for ext, folder in data.items():
            ext = ext.lower()
            if not ext.startswith('.'):
                ext = '.' + ext
            normalized[ext] = folder
        return normalized

    # To load rules from file
    def load_from_file(self, file_path: Path) -> None:
        """Loading rules from JSON-file"""
        try:
            with open(file_path, encoding='utf-8') as file:
                data = json.load(file)

                # Checking content frmo data
                if not isinstance(data, dict):
                    raise RuleError('File of rules must contain dict')
                # normalizing extentions in dict
                normalized = self.normalize_dict(data)
                self.__rules.update(normalized)
        except (IOError, json.JSONDecodeError) as exc:
            raise RuleError(f'Error while loading rules from:\nFile: {file_path}\nError: {exc}')

    # Loads defaults rules
    def load_defaults(self):
        """
        Loads default rules in default_rules.json if it exists
        else loads basic integrated rules
        """
        default_file = self.DEFAULT_RULES_FILE
        # 1.Scenario: if path file exists
        if default_file.exists():
            self.load_from_file(default_file)
        # 2.Sceanrio: if not
        else:
            # Integrated basic rules
            self.__rules.update(
                {
                    '.jpg': 'Images',
                    '.jpeg': 'Images',
                    '.png': 'Images',
                    '.gif': 'Images',
                    '.txt': 'Documents',
                    '.pdf': 'Documents',
                    '.docx': 'Documents',
                    '.mp3': 'Music',
                    '.wav': 'Music',
                    '.mp4': 'Videos',
                    '.avi': 'Videos',
                    '.zip': 'Archives',
                    '.rar': 'Archives',
                }
            )

    # Getting folder of extension
    def get_folder(self, extension: str) -> str:
        """Returns ext folder name in dict of rules"""
        ext = extension.lower()
        return self.__rules.get(ext, 'Others')
