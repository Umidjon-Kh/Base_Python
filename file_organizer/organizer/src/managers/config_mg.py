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

        # 2.Action: Loading default rules and styles dict
        default_rules = self.__loader.load_from_json('rules')
        default_styles = self.__loader.load_from_json('styles')

        # 3.Action: getting all configs blocks
        rules_cfg = configs.pop('rule_cfg', {})
        logger_cfg = configs.pop('logger_cfg', {})

        # 4.ACtion: Loading all data:
        # rules and styles from custom path
        # Checking rules file if its not None
        rules_data = None
        rules_file = rules_cfg.pop('rules_file')
        if rules_file is not None:
            temp_data = self.__loader.load_from_json('rules', rules_file)
            if rules_cfg.pop('combine', False):
                rules_data = self.__packer.deep_merge(default_rules, temp_data)
            else:
                rules_data = temp_data
        # Setting new rules for rules config
        rules_cfg['rules_data'] = rules_data if rules_data is not None else default_rules
        configs['rule_cfg'] = rules_cfg
        # Checking styles file if its not None
        styles_data = None
        styles_file = logger_cfg.pop('styles_file')
        if styles_file is not None:
            temp_file = self.__loader.load_from_json('sytles', styles_file)
            temp_data = logger_cfg.pop('styles_data', {}) or {}
            data = self.__packer.deep_merge(temp_file, temp_data)
            if logger_cfg.pop('combine', False):
                styles_data = self.__packer.deep_merge(default_styles, data)
            else:
                styles_data = data
        # Setting new styles for logger config
        logger_cfg['styles_data'] = styles_data if styles_data is not None else default_styles
        configs['logger_cfg'] = logger_cfg

        # 5.Action: Normalzing and validating all cfg params
        normalized_cfg = self.__normalizer.normalize_all_data(configs)
        # After normalizing we need to add rules to rules data if it exists
        normalized_cfg['rule_cfg']['rules_data'].update(configs['rule_cfg'].pop('rules', {}) or {})
        # Creating real configs
        self.__configs = normalized_cfg

    @property
    def configs(self) -> Dict[str, Any]:
        """Returns copy of configs"""
        return self.__configs.copy()
