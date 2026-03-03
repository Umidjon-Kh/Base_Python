from typing import Optional, Any, Dict

# Project modules
from ..tools import Normalizer, Packer, Loader


class ConfigManager:
    """
    Manages all Configs for:
    1) Core
    2) RuleMnager
    3) LogManager
    """

    __slots__ = ('__configs', '__normalizer', '__packer', '__loader')

    def __init__(self, args: Optional[Any], custom_cfg_path: Optional[str]) -> None:
        """
        Initialize configs from cli args and custom_cfg_path to load
        Calls method to load, normalize and pack all params into a one config
        """

        self.__normalizer = Normalizer()
        self.__packer = Packer()
        self.__loader = Loader()
        # self.__configs = {}

        # 1.Action: Loading all configs and packing into a one cfg
        if args is not None:
            configs = self.__packer.pack_args(args)
        elif custom_cfg_path is not None:
            configs = self.__packer.pack_custom_cfg(custom_cfg_path)
        else:
            configs = self.__loader.load_from_json('config')

        # 2.Action: Loading all custom rules and styles
        # Rules
        if configs['rule_cfg']['rules_file'] is not None:
            rules_file = configs['rule_cfg'].pop('rules_file')
            configs['rule_cfg']['rules_data'] = self.__loader.load_from_json('rules', rules_file)
        # Log Styles
        if configs['logger_cfg']['styles_file'] is not None:
            styles_file = configs['logger_cfg'].pop('styles_file')
            styles_data = self.__loader.load_from_json('styles')
            styles_data.update(self.__loader.load_from_json('styles', styles_file))
            styles_data.update(configs['logger_cfg']['styles_data'] or {})
            configs['logger_cfg']['styles_data'] = styles_data

        # 3.Action: Normalizing all data
        configs = self.__normalizer.normalize_all_data(configs)

        # 4.Action: Creating real configs dict with corrected and loaded data
        # Adding custom rules from args to rules_data
        additional_rules = configs['rule_cfg'].pop('rules')
        if additional_rules is not None:
            configs['rule_cfg']['rules_data'].update(additional_rules)
        # Creating default rules dict and adding it to rule cfg
        configs['rule_cfg']['default_rules'] = self.__loader.load_from_json('rules')
        # Creating real configs
        self.__configs = configs

    @property
    def configs(self) -> Dict[str, Any]:
        """Returns copy of configs"""
        return self.__configs.copy()
