from typing import Dict, Any

# Project modules
from ..exceptions import ConfigError
from .loader import Loader


class Packer:
    @staticmethod
    def pack_custom_cfg(custom_cfg_path: str) -> Dict[str, Any]:
        """Returns custom and default config combined and packed in one"""
        custom_config = Loader().load_from_json('config', custom_cfg_path)
        default_config = Loader().load_from_json('config')
        default_config.update(custom_config)
        return default_config

    @staticmethod
    def pack_args(args: Any) -> Dict[str, Any]:
        """Returns args converted to dict format and combined with default config pack"""
        config = {}
        # Converting args to dict
        args_dict = vars(args)

        # Main Organizer config params
        source = args_dict.get('source', None)
        # Checking source is not None
        if source is None:
            raise ConfigError('Arguments must contain Source param to run organizer')
        dest = args_dict.get('dest', None)
        dry_run = args_dict.get('dry_run', False)
        recursive = args_dict.get('recursive', False)
        clean = args_dict.get('clean', False)

        # Rule params
        rules = args_dict.get('rules', None)
        rules_file = args_dict.get('rules_file', None)
        combine = args_dict.get('combine', False)

        # Log params
        stream_level = args_dict.get('stream_level', 'debug')
        log_file = args_dict.get('log_file', None)
        enabled = True if log_file else False
        write_level = args_dict.get('write_level', 'debug')
        style = args.get('style', 'simple')
        cfg_file = args.get('config', None)
        # If cfg is not none loading file from path
        if cfg_file is not None:
            config = Loader().load_from_json('config', cfg_file)
            if not isinstance(config, dict):
                raise ConfigError('Config file must contain dict format data')

        # Setting all params to config
        config.update(
            {
                'core_cfg': {
                    'source': source,
                    'dest': dest,
                    'recursive': recursive,
                    'dry_run': dry_run,
                    'clean': clean,
                },
                'rule_cfg': {'rules': rules, 'rules_file': rules_file, 'combine': combine},
                'logger_cfg': {
                    'console': {'level': stream_level, 'style': style},
                    'file': {'enabled': enabled, 'path': log_file, 'level': write_level},
                },
            }
        )
        # Packing all configs in one with defaults
        default_config = Loader().load_from_json('config')
        default_config.update(config)

        return default_config
