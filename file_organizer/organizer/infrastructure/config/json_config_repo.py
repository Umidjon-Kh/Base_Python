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

    The JSON file must contain the following fields:
        - source_dir (str): path to source directory
        - dest_dir (str): path to destination directory
    Optional fields:
        - dry_run (bool): default false
        - recursive (bool): default true
        - ignore_patterns (list[str]): default none
        - rules_file (str): path to rules JSON (relative paths resolved relative to config file)
        - styles_file (str): path to styles JSON (relative paths resolved relative to config file)
        - logging (dict): logging configuration

    All paths are converted to absolute paths using the location of the config file
    as the base for relative paths.
    """

    def __init__(self, file_path: Union[Path, str]):
        """
        Args:
            file_path: Path to the JSON configuration file.
        """
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

        # Helper to resolve relative paths
        config_dir = self._file_path.parent

        def resolve_path(path_str: Optional[str]) -> Optional[Path]:
            if path_str is None:
                return None
            path = Path(path_str)
            if path.is_absolute():
                return path
            return (config_dir / path).resolve()

        # Extract and validate required fields
        try:
            source_dir = resolve_path(data.get('source_dir', None))
            if source_dir is None:
                raise ConfigValidationError('source_dir is required')
            dest_dir = resolve_path(data.get('dest_dir', None))
            if dest_dir is None:
                raise ConfigValidationError('dest_dir is required')
        except KeyError as exc:
            raise ConfigValidationError(f'Missing required field: {exc}') from exc

        # Optional fields
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

        rules_file = resolve_path(data.get('rules_file'))
        styles_file = resolve_path(data.get('styles_file'))
        logging_config = data.get('logging')
        if logging_config is not None and not isinstance(logging_config, dict):
            raise ConfigValidationError('logging must be a dictionary')

        # Create AppConfig (its own __init__ will validate absolute paths and types)
        return AppConfig(
            source_dir=source_dir,
            dest_dir=dest_dir,
            dry_run=dry_run,
            recursive=recursive,
            ignore_patterns=ignore_patterns,
            rules_file=rules_file,
            styles_file=styles_file,
            logging=logging_config,
        )
