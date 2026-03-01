from typing import Dict, Optional

# Project modules
from .rule_loader import RuleLoader


# class to configure rules of organizer
class RuleManager:
    """
    Manages with rules of sort: ext -> folder
    Auto adds User Custom rules from cli and rules file path
    to Rules, User Rules always Priority higher than default rules
    """

    __slots__ = ('__rules', '__rule_loader')

    def __init__(
        self, rules: Optional[Dict[str, str]] = None, rules_path: Optional[str] = None, combine: bool = False
    ) -> None:

        self.__rules = {}
        self.__rule_loader = RuleLoader()
        # 1.Action: combines default and user custom rules
        if combine:
            self.__rules.update(self.__rule_loader.load_rules())
        # 2.Action: Loading rules form file if it added
        if rules_path:
            normalized = self._normalize_dict(self.__rule_loader.load_rules(rules_path))
            self.__rules.update(normalized)
        # 3.Action: Adding user rules to dict
        if rules:
            normalized = self._normalize_dict(rules)
            self.__rules.update(normalized)
        # 4.Action: Setting default rules if not entered
        if not self.__rules:
            self.__rules.update(self.__rule_loader.load_rules())

    def get_folder(self, extension: str) -> str:
        """Returns ext folder name in dict of rules"""
        ext = extension.lower()
        return self.__rules.get(ext, 'Others')

    @staticmethod
    def _normalize_dict(data: Dict[str, str]) -> Dict[str, str]:
        """Returns right format dict of rules"""
        normalized = {}
        for ext, folder in data.items():
            ext = ext.lower()
            if not ext.startswith('.'):
                ext = '.' + ext
            normalized[ext] = folder
        return normalized
