from typing import Dict, Any


class RuleManager:
    """
    Manages with rules of sort: ext -> folder
    Auto adds User Custom rules from cli and rules data
    to Rules, User Rules always priority higher than default
    """

    __slots__ = ('__rules_data',)

    def __init__(self, config: Dict[str, Any]) -> None:
        # Initializing a
        rules_data = config.get('rules_data', {})
        if config.get('combine', False):
            default_rules = config.get('default_rules', {})
            rules_data.update(default_rules)
        self.__rules_data = config

    def get_folder(self, extension: str) -> str:
        """Returns ext folder name in dict of rules"""
        ext = extension.lower()
        return self.__rules_data.get(ext, 'Other')
