from typing import Dict, Optional

# Project modules
from ..tools import ConfigNormalizer, Loader


# class to configure rules of organizer
class RuleManager:
    """
    Manages with rules of sort: ext -> folder
    Auto adds User Custom rules from cli and rules file path
    to Rules, User Rules always Priority higher than default rules
    """

    __slots__ = ('__rules', '__loader', '__normalizer')

    def __init__(
        self, rules: Optional[Dict[str, str]] = None, rules_path: Optional[str] = None, combine: bool = False
    ) -> None:

        self.__rules = {}
        self.__loader = Loader()
        self.__normalizer = ConfigNormalizer()
        # 1.Action: combines default and user custom rules
        if combine:
            self.__rules.update(self.__loader.load_from_file('rules'))
        # 2.Action: Loading rules form file if it added
        if rules_path:
            data = self.__loader.load_from_file('rules', rules_path)
            normalized = self.__normalizer.data_normalizer(data, 'rule_mg')
            self.__rules.update(normalized)
        # 3.Action: Adding user rules to dict
        if rules:
            normalized = self.__normalizer.data_normalizer(rules, 'rule_mg')
            self.__rules.update(normalized)
        # 4.Action: Setting default rules if not entered
        if not self.__rules:
            self.__rules.update(self.__loader.load_from_file('rules'))

    def get_folder(self, extension: str) -> str:
        """Returns ext folder name in dict of rules"""
        ext = extension.lower()
        return self.__rules.get(ext, 'Others')
