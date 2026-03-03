from ast import literal_eval
from typing import Dict, Any, Tuple

# project modules
from ..exceptions import ConfigError, RuleError


class Normalizer:
    """Normalizes all configs params and returns in right format"""

    @classmethod
    def normalize_all_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Returns data configs in normalized format"""
        normalized_data = {}
        for cfg_type, params in data.items():
            params = cls.data_normalizer(params, cfg_type)
            normalized_data[cfg_type] = params
        return normalized_data

    @classmethod
    def data_normalizer(cls, params: Dict[str, Any], cfg_type: str) -> Dict[str, Any]:
        """
        Returns normalized params for configs type:
        1) Core configs: Main organizer params
        2) RuleManager configs: dict of rules
        3) LogManager configs: dict of log params
        """

        normalized_params = {}
        for param, value in params.items():
            if cfg_type == 'rule_cfg' and value is not None:
                if param == 'rules':
                    value = cls.rule_checker(value)
                    value = cls.rules_normalizer(value)
                elif param == 'combine':
                    param, value = cls.boolean_checker(param, value)
                else:
                    value = cls.rules_normalizer(value)
            if cfg_type == 'logger_cfg' and param in ('console', 'file'):
                param, value = cls.log_param_normalizer(param, value)
            if cfg_type == 'core_cfg':
                if param not in ('source', 'dest'):
                    param, value = cls.boolean_checker(param, value)
            normalized_params[param] = value
        return normalized_params

    @staticmethod
    def boolean_checker(param: str, value: Any) -> Tuple[str, bool]:
        if not isinstance(value, bool):
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            else:
                raise ConfigError(f'Param: \'{param}\' must be boolean type (true/false)')
        return param, value

    @staticmethod
    def rule_checker(rules: Any) -> Dict[str, str]:
        """Checks and returns rules from args if it in right format"""
        try:
            rules_dict = literal_eval(rules)
            if not isinstance(rules_dict, dict):
                raise ConfigError('Param \'rules\' value must be in dict format(\'.png\': \'PNG\')')
            return rules_dict
        except (SyntaxError, ValueError) as exc:
            raise RuleError(f'Wrong format of rules param: {exc}')

    @staticmethod
    def rules_normalizer(rules: Dict[str, str]) -> Dict[str, str]:
        """Normalizes all rules dict: extention to work properly"""
        normalized_rules = {}
        for ext, folder in rules.items():
            ext = ext.lower()
            if not ext.startswith('.'):
                ext = '.' + ext
            normalized_rules[ext] = folder
        return normalized_rules

    @staticmethod
    def log_param_normalizer(handler: str, params) -> Tuple[str, Dict]:
        """Returns validated and right formated of configs params for log"""
        # Validating console log handler configs
        if handler == 'console' and params.get('enabled', True):
            for param, value in params.items():
                if param not in ('enabled', 'level', 'colorize', 'style'):
                    raise ConfigError(f'LogManager console handler config param \'{param}\' is unacceptable')
                if param in ('colorize', 'enabled'):
                    if not isinstance(value, bool):
                        raise ConfigError(f'Param: \'{param}\' value must be bool type')
        # Validating file log handler
        elif handler == 'file' and params.get('enabled', False):
            for param, value in params.items():
                if param not in (
                    'enabled',
                    'level',
                    'style',
                    'path',
                    'rotation',
                    'retention',
                    'compression',
                ):
                    raise ConfigError(f'LogManager file handler config param \'{param}\' is unacceptable')
                if param == 'enabled' and not isinstance(value, bool):
                    raise ConfigError(f'Param: \'{param}\' value must be bool type')
            # Checking path if file handler is enabled
            if params.get('path', None) is None:
                raise ConfigError('File handler config must contain path to save if its enabled')
        return handler, params
