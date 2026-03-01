from ast import literal_eval
from typing import Optional, Any, Dict

# Project modules
from ..tools import Loader, ConfigNormalizer
from .exceptions import ConfigError


class ConfigManager:
    """
    Manages all Configs for
    LogManager, RuleManager and Main core Organizer
    """

    __slots__ = ('__configs', '__loader', '__normalizer')

    def __init__(self, args: Optional[Any], config_path: Optional[str]) -> None:
        """
        Initialize configs dict and args,
        Calls method to load and normalize all data in configs
        """

        self.__configs = {}
        self.__loader = Loader()
        self.__normalizer = ConfigNormalizer()

        # 1.Action: Loading default configs
        self.__configs = self.__loader.load_from_file('config')
        # 2.Action: If config path is not None
        if config_path:
            data = self.__loader.load_from_file('config', config_path)
            normalized = self.__normalizer.data_normalizer(data, 'config_mg')
            self.__configs.update(normalized)

        # 3.Actio: Adding args for configs
        if args:
            self.__configs.update(vars(args))
            self.__configs.pop('config', None)

        # 4.Action: Checking source is not None
        self.source_checker()
        # 5.Action: Checking rules if its not None
        if self.__configs['rules'] is not None:
            self.arg_rules_checker()

    @property
    def configs(self) -> Dict:
        """Returns copy of configs to safety"""
        return self.__configs.copy()

    def source_checker(self) -> None:
        """Checks Source path None or not"""
        if self.__configs['source'] is None:
            raise ConfigError('ConfigManager configs must contain source argument')

    def arg_rules_checker(self) -> None:
        """Checks rules for right format"""
        rules_dict = literal_eval(self.__configs['rules'])
        try:
            if not isinstance(rules_dict, dict):
                raise ConfigError('Argument rules must be type of dict object, e.g.: "{\'.png\': \'PNG\'}"')
        except (SyntaxError, ValueError):
            raise ConfigError('Wrong format of rules argument, e.g.: "{\'png\': \'PNG\'}"')
