from typing import Dict, Any

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

    def __init__(self, config: Dict[str, Any]) -> None:

        self.__rules = {}
        self.__loader = Loader()
        self.__normalizer = ConfigNormalizer()
        # Unpacking all args from config dict
        self.config_unpacker(config)

    def get_folder(self, extension: str) -> str:
        """Returns ext folder name in dict of rules"""
        ext = extension.lower()
        return self.__rules.get(ext, 'Others')

    def config_unpacker(self, config: Dict[str, Any]) -> None:
        """Unpacking configs dict got from Config manager"""
        if config:
            # 1.Action: combines default and user custom rules
            if config.get('combine', False):
                self.__rules.update(self.__loader.load_from_json('rules'))
            # 2.Action: Loading rules form file if it added
            if config.get('rules_path', None) is not None:
                data = self.__loader.load_from_json('rules', config['rules_path'])
                normalized = self.__normalizer.data_normalizer(data, 'rule_mg')
                self.__rules.update(normalized)
            # 3.Action: Adding user rules to dict
            if config.get('rules', None) is not None:
                normalized = self.__normalizer.data_normalizer(config['rules'], 'rule_mg')
                self.__rules.update(normalized)
            # 4.Action: Setting default rules if not entered
            if not self.__rules:
                self.__rules.update(self.__loader.load_from_json('rules'))
