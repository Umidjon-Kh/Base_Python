"""
bootstrap.py - Composition Root of the entire application

------------------------------------------------------
| Role of this file in the Architecture              |
------------------------------------------------------
This file is Composition Root - the single place in the codebase that:
    + knows about all layers of codebase (domain, applicatio, infrastructure, ...)
    + creates every concrete object (adapters, loggers, repositories, ...)
    + injects those objects into a use cases via port interfaces (DI: Dependency Injection)

All other modules respect the strict layering rules
    domain          | knows nothing
    application     | knows only domain
    infrastructure  | knows application ports, interfaces(AppConfig, ...) + domain
    bootstrap       | knows everything (intentionally, this is its purpose)

-----------------------------------------------------
| Why ConfigOverrides class is for?!                |
-----------------------------------------------------

bootstrap() receives a ConfigOverrides dataclass, Cause:
This enables multiply entry points without changing logic of bootstrap(),
    in the future you can add multiple interfaces like (WEB, Tkinter, QT other GUI and etc...)
    right now i only have CLI interface
        interfaces/cli/main.py -> fills ConfigOverrider from argparse args


---------------------------------------------------------
| Config Merging Strategy and Priority of Config layers |
---------------------------------------------------------
| Low Priority    | Layer 1 | data/config.json          | default values
| Medium Priority | Layer 2 | overrides.confile_file    | user's own file repos
| Hight Priority  | Layer 3 | remaining ConfigOverrides | individual field overrides

Rule: a field from layer replaces the same field from lower
layer only if the higher value is not None
"""

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Optional, Union

# Application layer - config data class and port interface only
from .application import AppConfig

# Infrastructure layer - concrete adapters that implement the ports
from .infrastructure import (
    InMemoryConfigRepository,
    JsonConfigRepository,
    InMemoryRuleRepository,
    JsonRuleRepository,
    InMemoryStyleRepository,
    JsonStyleRepository,
    LoguruLogger,
    OSFileSystem,
)

# Excpetions
from .exceptions import ConfigValidationError, InvalidPathError


# Default config repo file paths
_DEFAULT_CONFIG_PATH: Path = Path(__file__).parent / 'data' / 'config.json'
_DEFAULT_RULES_PATH: Path = Path(__file__).parent / 'data' / 'rules.json'
_DEFAULT_STYLES_PATH: Path = Path(__file__).parent / 'data' / 'styles.json'

# class ConfigOverrides


# I skipped dataclasses in this project as
# I was unfamiliar with the library during development.
# I only did some light research while creating ConfigOverrider and AppConfig,
# hence their absence here.
class ConfigOverrides:
    """
    Neutral DTo between any entry point and bootstrap().

    Every fiedls defaults to None = 'not provided, keep whatever lower layers say'.
    Only non-None values actually override something in the merged AppConfig.

    Who creates this:
        This class ordinary creates only entry points cause they need to push all user
        args and configs to main code

        interface/cli/main.py  - from argparse args
        interface/gui/main.py  - from widgets values
        tests                  - directly with specific values

    Who consumes this:
        bootstrap() / _build_config() - and nobody else
    """

    def __init__(
        self,
        # Path overrides
        source_dir: Optional[Union[Path, str]] = None,
        dest_dir: Optional[Union[Path, str]] = None,
        config_files: Optional[Union[Path, str]] = None,
        rules_file: Optional[Union[Path, str]] = None,
        styles_file: Optional[Union[Path, str]] = None,
        log_file: Optional[Union[Path, str]] = None,
        # Config overrides
        rules_cfg: Optional[Dict[str, Any]] = None,
        styles_cfg: Optional[Dict[str, Any]] = None,
        # Booleans
        dry_run: Optional[bool] = None,
        recursive: Optional[bool] = None,
        rules_combine: Optional[bool] = None,
        styles_combine: Optional[bool] = None,
        # Logging level overrides
        console_level: Optional[str] = None,
        file_level: Optional[str] = None,
        # Full logging dict config override
        logging: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.source_dir = source_dir
        self.dest_dir = dest_dir
        self.config_files = config_files
        self.rules_file = rules_file
        self.styles_file = styles_file
        self.log_file = log_file
        self.rules_cfg = rules_cfg
        self.styles_cfg = styles_cfg
        self.dry_run = dry_run
        self.recursive = recursive
        self.rules_combine = rules_combine
        self.styles_combine = styles_combine
        self.console_level = console_level
        self.file_level = file_level
        self.logging = logging


# Internal helpers


def _resolve(path: Optional[Union[Path, str]]) -> Optional[Path]:
    """
    Expand ~ and make path absolute. Returns None unchenged.
    AppConfig requires absolute paths - this ensures that before we pass anything in.
    """

    if path is None:
        return None
    if isinstance(path, str):
        path = Path(path)
    return path.expanduser().resolve()


def _merge_logging(
    base: Optional[Dict[str, Any]],
    full_override: Optional[Dict[str, Any]],
    log_file: Optional[Union[Path, str]],
    console_level: Optional[str],
    file_level: Optional[str],
) -> Optional[Dict[str, Any]]:
    """
    Produce the final logging config dict

    Priority (highest first):
        1. full_override - complete logging dict use as-is
        2. individual overries (log_file, console_level, file_level) -> patch base
        3. base          - whatever came from config repo loader -> keep unchaged
    """
    # Case 1: If full_override is provided return copy of it
    if full_override is not None:
        return deepcopy(full_override)

    # Case 2: path individual fields
    # Use is not None not thruthines - empty string is still a user-supplied value
    if console_level is not None or log_file is not None or file_level is not None:
        merged = deepcopy(base or {})

        # Overwriting console level if its not None
        if console_level is not None:
            console_block = merged.get('console', {})
            console_block['enabled'] = True
            console_block['level'] = console_level
            merged['console'] = console_block

        # Overwriting log file path pr file log level if one of them provided
        if log_file is not None or file_level is not None:
            file_block = merged.get('file', {})
            file_block['enabled'] = True
            if log_file is not None:
                file_block['path'] = str(log_file)
            if file_level is not None:
                file_block['level'] = file_level
            merged['file'] = file_block

        return merged

    # Case 3: nothing to override
    return base


# -------- Step 1: Build the final merged AppConfig --------
def _build_config(overrides: ConfigOverrides) -> AppConfig:
    """
    Merge three config layers into a single AppConfig.

    Layer 1: data/config.json       - default values
    Layer 2: overrides.config_file  - user's own config repo
    Layer 3: ConfigOverrides fields - individual overrides


    Raises:
        ConfigValidationError: If source_dir is still None after all layers
    """

    # Layer 1: default config
    base: AppConfig = JsonConfigRepository(_DEFAULT_CONFIG_PATH).load_config()

    # Layer 2: User Repo config file
    config_path = _resolve(overrides.config_files)
    if config_path is not None:
        # checking for config file extension type
        match config_path.suffix.lower():
            case '.json':  # if JSON file type
                base = JsonConfigRepository(config_path).load_config()
            case _:
                raise InvalidPathError(f'Wrong type of path file: {config_path=}')

    # Layer 3: Individual field overrides
    # Pattern for paths: use override if not None, otherwise keep base value
    source_dir = _resolve(overrides.source_dir) or base.source_dir
    dest_dir = _resolve(overrides.dest_dir) or base.dest_dir
    rules_file = _resolve(overrides.rules_file) or base.rules_file
    styles_file = _resolve(overrides.styles_file) or base.styles_file

    # Dicts: use `is not None` because an empty dict {} is a valid override
    rules_cfg = overrides.rules_cfg if overrides.rules_cfg is not None else base.rules_cfg
    styles_cfg = overrides.styles_cfg if overrides.styles_cfg is not None else base.styles_cfg

    # Booleans: MUST use `is not None` - False is a valid explicit override
    # `False or base.dry_run` would incorrectly discard an explicit False
    dry_run = overrides.dry_run if overrides.dry_run is not None else base.dry_run
    recursive = overrides.recursive if overrides.recursive is not None else base.recursive
    rules_combine = overrides.rules_combine if overrides.rules_combine is not None else base.rules_combine
    styles_combine = overrides.styles_combine if overrides.styles_combine is not None else base.styles_combine

    # Logging: delegate to _merge_logging which handles all sub-cases
    logging_cfg = _merge_logging(
        base=base.logging,
        full_override=overrides.logging,
        log_file=_resolve(overrides.log_file),
        console_level=overrides.console_level,
        file_level=overrides.file_level,
    )

    # Validation
    if source_dir is None:
        raise ConfigValidationError(
            'source_dir is required but was not found in any config layer.\n'
            'Provide it via:\n'
            '  • data/config.json        ("source_dir" key)\n'
            '  • --config file           ("source_dir" key)\n'
            '  • positional CLI argument (python -m organizer /path/to/dir)\n'
            '  • GUI source directory widget'
        )

    # Retruning completely builded(merged/overrided) config AppConfig
    return AppConfig(
        source_dir=source_dir,
        dest_dir=dest_dir,
        dry_run=dry_run,
        recursive=recursive,
        ignore_patterns=base.ignore_patterns,
        rules_file=rules_file,
        rules_cfg=rules_cfg,
        rules_combine=rules_combine,
        styles_file=styles_file,
        styles_cfg=styles_cfg,
        styles_combine=styles_combine,
        logging=logging_cfg,
    )


# ----------- Step 2: Wire all dependencies and run the app


def bootstrap(overrides: ConfigOverrides) -> None:
    """
    Composition Root: create every dependency and launch application

    THe only function that instantiates infrastructure adapters.
    Use cases receive everything through port interface (Dependency Injection).

    Wiring order:
        1. Merge config layers      --> AppConfig
        2. Wrap AppConfig           --> InMemoryConfigRepository
        3. Pick rules adapters      --> RuleRepository(InMemoryRepository)
        4. Pick rstyles adapters    --> StyleRepository(InMemoryRepository)
        5. Build Styleset + Logger  --> Logger(right now only LoguruLogger)
        6. Build FileSystem adapter --> FileSystem(right now only OSFileSystem)
        7. Run use case
    """

    # 1. Final Merged config
    config: AppConfig = _build_config(overrides)

    # 2. Config Repository
    # All merging is done. Wrap the final AppConfig so use case get it
    # through the ConfigRepository port without knowing how it was built.
    config_repo = InMemoryConfigRepository(config)

    # 3. Rules Repository
    default_rules_repo = JsonRuleRepository(_DEFAULT_RULES_PATH)

    # Match/Casing user rules file to inject it to RuleRepository
    user_rules_repo = None
    if config.rules_file is not None:
        match config.rules_file.suffix.lower():
            case '.json':  # if JSON file type
                user_rules_repo = JsonRuleRepository(config.rules_file)
            case _:
                raise InvalidPathError(f'Wrong type of path file: {config.rules_file=}')

    # Creating main RuleRepository
    rule_repo = InMemoryRuleRepository(
        default_repo=default_rules_repo,
        rules_repo=user_rules_repo,
        rules_cfg=config.rules_cfg,
        combine=config.rules_combine or False,
    )

    # 4. Styles Repository
    # Same as injecting RuleRepo
    default_styles_repo = JsonStyleRepository(_DEFAULT_STYLES_PATH)

    # Match/Casing user styles file to inject it to StyleRepository
    user_styles_repo = None
    if config.styles_file is not None:
        match config.styles_file.suffix.lower():
            case '.json':  # If JSON file type
                user_styles_repo = JsonStyleRepository(config.styles_file)
            case _:
                raise InvalidPathError(f'Wrong type of path file: {config.styles_file=}')

    # Creating main StyleRepository
    style_repo = InMemoryStyleRepository(
        default_repo=default_styles_repo,
        styles_repo=user_styles_repo,
        styles_data=config.styles_cfg,
        combine=config.styles_combine or False,
    )

    # 5. Logger
    # config.logging is already fully merged by _build_config()
    # Fallback if All config layers han no logging section at all
    style_set = style_repo.load_styles()
    logging_cfg = config.logging or {}
    logger = LoguruLogger(logging_cfg, style_set)

    # 6. FileSystem adapter
    file_system = OSFileSystem()