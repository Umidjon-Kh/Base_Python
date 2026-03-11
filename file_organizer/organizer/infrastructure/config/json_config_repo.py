import json
from pathlib import Path
from typing import Union, Optional

from ...application import ConfigRepository, AppConfig
from ...exceptions import (
    ConfigNotFoundError,
    ConfigFormatError,
    ConfigValidationError,
)


class JsonConfigRepository(ConfigRepository):
    """
    Loads configuration from a JSON file.

    Required fields:
        source_dir (str), dest_dir (str)

    Optional fields:
        dry_run, recursive, ignore_patterns, logging

    Rules block — data['rules']:
        rules_cfg  (dict):  inline rules config
        rules_repo (str):   path to external rules JSON file
        combine    (bool):  whether to combine with default rules

    Styles block — data['styles']:
        styles     (dict):  inline styles config
        styles_repo(str):   path to external styles JSON file
        combine    (bool):  whether to combine with default styles
    """
    __slots__ = ('_file_path')

    def __init__(self, file_path: Union[Path, str]):
        self._file_path = Path(file_path)

    def load_config(self) -> AppConfig:
        if not self._file_path.exists():
            raise ConfigNotFoundError(f'Config file not found: {self._file_path}')

        try:
            with open(self._file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except (IOError, json.JSONDecodeError) as exc:
            raise ConfigFormatError(f'Invalid JSON in config file: {exc}') from exc

        if not isinstance(data, dict):
            raise ConfigFormatError('Config file must contain a JSON object')

        config_dir = self._file_path.parent

        def resolve_path(path_str: Optional[str]) -> Optional[Path]:
            if path_str is None:
                return None
            path = Path(path_str)
            if path.is_absolute():
                return path
            return (config_dir / path).resolve()

        # Optional main organization path fields
        source_dir = resolve_path(data.get('source_dir', None))
        dest_dir = resolve_path(data.get('dest_dir', None))

        # Optional fields for organizer modes and ignore patterns
        dry_run = data.get('dry_run', False)
        if not isinstance(dry_run, bool):
            raise ConfigValidationError('dry_run must be a boolean')

        recursive = data.get('recursive', True)
        if not isinstance(recursive, bool):
            raise ConfigValidationError('recursive must be a boolean')

        ignore_patterns = data.get('ignore_patterns')
        if ignore_patterns is not None:
            if not isinstance(ignore_patterns, list):
                raise ConfigValidationError('ignore_patterns must be a list')
            for pat in ignore_patterns:
                if not isinstance(pat, str):
                    raise ConfigValidationError('each ignore pattern must be a string')

        # Logging config fields
        logging_cfg = data.get('logging')
        if logging_cfg is not None and not isinstance(logging_cfg, dict):
            raise ConfigValidationError('logging must be a dictionary')

        # Rules config fields
        # First get the whole rules block, then extract fields from it
        rules_block = data.get('rules')
        if rules_block is not None and not isinstance(rules_block, dict):
            raise ConfigValidationError('rules must be a dictionary block')

        rules_cfg = None
        rules_file = None
        rules_combine = False
        if rules_block is not None:
            rules_cfg = rules_block.get('rules_cfg')
            rules_file = resolve_path(rules_block.get('rules_repo'))
            rules_combine = rules_block.get('combine', False)
            if rules_cfg is not None and not isinstance(rules_cfg, dict):
                raise ConfigValidationError('rules.rules_cfg must be a dictionary')
            if not isinstance(rules_combine, bool):
                raise ConfigValidationError('rules.combine must be a boolean')

        # Styles config fields
        # Same pattern as rules block
        styles_block = data.get('styles')
        if styles_block is not None and not isinstance(styles_block, dict):
            raise ConfigValidationError('styles must be a dictionary block')

        styles_cfg = None
        styles_file = None
        styles_combine = False
        if styles_block is not None:
            styles_cfg = styles_block.get('styles')
            styles_file = resolve_path(styles_block.get('styles_repo'))
            styles_combine = styles_block.get('combine', False)
            if styles_cfg is not None and not isinstance(styles_cfg, dict):
                raise ConfigValidationError('styles.styles must be a dictionary')
            if not isinstance(styles_combine, bool):
                raise ConfigValidationError('styles.combine must be a boolean')

        return AppConfig(
            source_dir=source_dir,
            dest_dir=dest_dir,
            dry_run=dry_run,
            recursive=recursive,
            ignore_patterns=ignore_patterns,
            rules_file=rules_file,
            rules_cfg=rules_cfg,
            rules_combine=rules_combine,
            styles_file=styles_file,
            styles_cfg=styles_cfg,
            styles_combine=styles_combine,
            logging=logging_cfg,
        )
