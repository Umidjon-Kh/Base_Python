"""
bootstrap.py — Composition Root of the entire application.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ROLE OF THIS FILE IN THE ARCHITECTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This file is the Composition Root — the single place in the codebase that:
  • knows about ALL layers (domain, application, infrastructure)
  • creates every concrete object (adapters, loggers, repositories)
  • injects those objects into use cases via port interfaces (Dependency Injection)

All other modules respect the strict layering rule:
    domain        ←  knows nothing
    application   ←  knows only domain
    infrastructure←  knows application ports + domain
    bootstrap     ←  knows everything (intentionally, this is its purpose)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHY ConfigOverrides INSTEAD OF argparse.Namespace
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

bootstrap() receives a ConfigOverrides dataclass, NOT argparse.Namespace.
This is a deliberate design decision that enables multiple entry points:

    interface/cli/main.py   →  fills ConfigOverrides from argparse args
    interface/gui/main.py   →  fills ConfigOverrides from tkinter/qt widgets
                                      ↓
                               bootstrap(overrides)   ← same function, no changes

bootstrap() doesn't care WHERE the values came from. It only cares about
what values it received. This is the "Ports and Adapters" (hexagonal)
pattern applied at the entry-point level.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONFIG MERGING STRATEGY  (3 layers, each overrides the previous)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Layer 1 │ data/config.json        │ default values bundled with the package
  Layer 2 │ overrides.config_file   │ user's own JSON config  (optional)
  Layer 3 │ remaining ConfigOverrides fields │ individual value overrides

  Rule: a field from a higher layer replaces the same field from a lower
  layer ONLY if the higher-layer value is not None.

  Example:
      default config   → source_dir = ~/Pictures,  dry_run = False
      user config      → source_dir = ~/Downloads              (overrides L1)
      ConfigOverrides  → dry_run    = True                     (overrides L2)
      ─────────────────────────────────────────────────────────────────────
      FINAL AppConfig  → source_dir = ~/Downloads,  dry_run = True
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Union

# Application layer — config data class and port interfaces only
from organizer.application import AppConfig

# Infrastructure layer — concrete adapters that implement the ports
from organizer.infrastructure import (
    InMemoryConfigRepository,  # wraps a ready AppConfig so use cases get it via port
    JsonConfigRepository,  # reads AppConfig from a JSON file
    JsonRuleRepository,  # reads RuleSet from a JSON file
    JsonStyleRepository,  # reads StyleSet from a JSON file
    LoguruLogger,  # Logger port adapter backed by loguru
    OSFileSystem,  # FileSystem port adapter backed by pathlib / shutil
)
from organizer.exceptions import ConfigValidationError


# ─────────────────────────────────────────────────────────────────────────────
# Package-level default file paths
# ─────────────────────────────────────────────────────────────────────────────

# Path(__file__).parent  →  the organizer/ package directory
# These files are shipped together with the package and act as the baseline.
_DEFAULT_CONFIG_PATH: Path = Path(__file__).parent / 'data' / 'config.json'
_DEFAULT_RULES_PATH: Path = Path(__file__).parent / 'data' / 'rules.json'
_DEFAULT_STYLES_PATH: Path = Path(__file__).parent / 'data' / 'styles.json'


# ─────────────────────────────────────────────────────────────────────────────
# ConfigOverrides  —  neutral DTO between any entry point and bootstrap
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class ConfigOverrides:
    """
    A plain data container that carries user-supplied overrides into bootstrap().

    Every field defaults to None, which means "not provided — keep whatever
    the lower config layers say". Only non-None values actually override
    something in the merged AppConfig.

    WHO CREATES THIS OBJECT:
        interface/cli/main.py  — reads argparse args and fills the fields
        interface/gui/main.py  — reads widget values and fills the fields
        tests                  — created directly with specific values

    WHO CONSUMES THIS OBJECT:
        bootstrap() / _build_config()  — and nobody else

    ── Path fields ──────────────────────────────────────────────────────────
    source_dir    Override the directory to scan and organise.
    dest_dir      Override the root destination directory.
    config_file   Path to a user-supplied JSON config (Layer 2).
    rules_file    Override the JSON file that defines sorting rules.
    styles_file   Override the JSON file that defines log level styles.
    log_file      Inject a log-file path into the logging dict and enable it.

    ── Boolean fields ───────────────────────────────────────────────────────
    dry_run       If True, simulate without moving any files.
    no_recursive  If True, scan only the top level (disable recursion).

    ── Logging levels ───────────────────────────────────────────────────────
    console_level  Override default debug level of console log level
    file_level   Override default debug level of file log level

    ── Full logging override (used by GUI) ──────────────────────────────────
    logging       A complete logging config dict.  When the GUI allows the
                  user to customise log levels and styles interactively, it
                  builds this dict from widget values and passes it here.
                  If provided, it replaces the entire logging section that
                  came from the JSON layers — individual log_file is ignored.

                  Expected structure (same as config.json → "logging"):
                  {
                      "console": {"enabled": True, "level": "INFO"},
                      "file":    {"enabled": True, "level": "DEBUG",
                                  "path": "logs/app.log",
                                  "rotation": "1 day", "retention": "7 days"}
                  }
    """

    # Path overrides
    source_dir: Optional[Union[Path, str]] = None
    dest_dir: Optional[Union[Path, str]] = None
    config_file: Optional[Union[Path, str]] = None
    rules_file: Optional[Union[Path, str]] = None
    styles_file: Optional[Union[Path, str]] = None
    log_file: Optional[Union[Path, str]] = None

    # Boolean overrides
    dry_run: Optional[bool] = None
    no_recursive: Optional[bool] = None

    # Logging levels
    console_level: Optional[str] = None
    file_level: Optional[str] = None

    # Full logging dict override (GUI use case — replaces the whole logging section)
    logging: Optional[Dict[str, Any]] = None


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────


def _resolve(path: Optional[Union[Path, str]]) -> Optional[Path]:
    """
    Expand ~ and make a path absolute.  Returns None unchanged.

    Used everywhere we accept a user-supplied path, because:
      • argparse gives us whatever the user typed (relative or ~-prefixed)
      • AppConfig requires absolute paths and will raise if given a relative one
    """
    if path is None:
        return None
    if isinstance(path, str):
        path = Path(path)
    return path.expanduser().resolve()


def _merge_logging(
    base: Optional[Dict[str, Any]],
    full_override: Optional[Dict[str, Any]],
    log_file: Optional[Path],
    console_level: Optional[str],
    file_level: Optional[str],
) -> Optional[Dict[str, Any]]:
    """
    Produce the final logging config dict by applying overrides on top of base.

    Priority (highest first):
        1. full_override  — GUI passed a complete logging dict  → use it as-is
        2. log_file       — a single --log-file path was given  → patch file section
        3. base           — whatever came from the JSON layers  → keep unchanged

    Why deep copy?
        AppConfig stores the logging dict by reference.  Mutating it directly
        would silently corrupt the original config object, which is supposed to
        be immutable.  We always work on copies.

    Args:
        base:          The logging dict from the merged JSON layers (may be None).
        full_override: A complete logging dict from the GUI (may be None).
        log_file:      An absolute path to a log file from --log-file (may be None).

    Returns:
        The final logging dict ready to pass into AppConfig, or None if nothing
        was configured at all (bootstrap will apply a safe fallback later).
    """

    # Case 1: GUI provided a full logging dict — use it entirely, ignore the rest
    if full_override is not None:
        return copy.deepcopy(full_override)

    # Case 2: CLI provided --log-file and/or --console-level / --file-level
    #
    # We use `is not None` instead of truthiness checks because an empty
    # string would be falsy but is still a user-supplied (invalid) value
    # that should pass through and let loguru raise a clear error.
    if console_level is not None or log_file is not None or file_level is not None:
        merged = copy.deepcopy(base or {})  # deep-copy so we never mutate base

        # --console-level: override the console handler log level
        if console_level is not None:
            console_section = merged.get('console', {})
            console_section['enabled'] = True
            console_section['level'] = console_level
            merged['console'] = console_section

        # --log-file and/or --file-level: these are INDEPENDENT overrides.
        #
        # BUG that was here: file_level was nested inside `if log_file`,
        # so `--file-level DEBUG` alone (without --log-file) had no effect.
        # Fix: handle log_file and file_level in separate inner blocks under
        # one shared file_section, so either can work without the other.
        if log_file is not None or file_level is not None:
            file_section = merged.get('file', {})
            # --log-file: set the path and implicitly enable file logging
            if log_file is not None:
                file_section['path'] = str(log_file)  # loguru expects str, not Path
                file_section['enabled'] = True  # --log-file implicitly enables
            # --file-level: just change the level, leave enabled/path untouched
            if file_level is not None:
                file_section['level'] = file_level
            merged['file'] = file_section

        return merged

    # Case 3: nothing to override — return base as-is (already owned by AppConfig)
    return base


# ─────────────────────────────────────────────────────────────────────────────
# Step 1 — Build the final merged AppConfig from all three layers
# ─────────────────────────────────────────────────────────────────────────────


def _build_config(overrides: ConfigOverrides) -> AppConfig:
    """
    Merge three config layers into a single immutable AppConfig.

    Args:
        overrides: A ConfigOverrides instance from any entry point (CLI or GUI).

    Returns:
        A fully populated AppConfig ready for use.

    Raises:
        ConfigValidationError: if source_dir is still None after all layers.
        ConfigNotFoundError:   if a config JSON file does not exist.
        ConfigFormatError:     if a config JSON file has invalid structure.
    """

    # ── Layer 1: default config bundled with the package ──────────────────
    # This always loads first and provides safe baseline values for every
    # setting so that neither CLI nor GUI has to specify everything.
    base_config: AppConfig = JsonConfigRepository(_DEFAULT_CONFIG_PATH).load_config()

    # ── Layer 2: user's own JSON config file (optional) ───────────────────
    # If the user pointed us to their own config file, load it on top of
    # the default.  It can change any field — source_dir, dest_dir, rules,
    # logging, etc.  It becomes the new base for Layer 3 overrides.
    if overrides.config_file is not None:
        user_path = _resolve(overrides.config_file)
        base_config = JsonConfigRepository(user_path).load_config()  # type: ignore

    # ── Layer 3: individual field overrides from ConfigOverrides ──────────
    # For each field: use the override value when it is not None,
    # otherwise keep what Layer 1/2 gave us.
    #
    # Pattern:  _resolve(overrides.X) or base_config.X
    #   • _resolve() returns None when overrides.X is None  → fall back to base
    #   • _resolve() returns an absolute Path otherwise      → use that path

    source_dir = _resolve(overrides.source_dir) or base_config.source_dir
    dest_dir = _resolve(overrides.dest_dir) or base_config.dest_dir
    rules_file = _resolve(overrides.rules_file) or base_config.rules_file
    styles_file = _resolve(overrides.styles_file) or base_config.styles_file

    # Boolean overrides: None means "not set by this entry point, use config value"
    # We cannot use  `overrides.dry_run or base_config.dry_run`  here because
    # `False or base_config.dry_run` would incorrectly discard an explicit False.
    dry_run = overrides.dry_run if overrides.dry_run is not None else base_config.dry_run
    recursive = (not overrides.no_recursive) if overrides.no_recursive is not None else base_config.recursive

    # Logging dict: delegate to _merge_logging which handles all three sub-cases
    logging_cfg = _merge_logging(
        base=base_config.logging,
        full_override=overrides.logging,
        log_file=_resolve(overrides.log_file),
        console_level=overrides.console_level,
        file_level=overrides.file_level,
    )

    # ── Validation ────────────────────────────────────────────────────────
    # source_dir is the only field with no sensible universal default.
    # Every other field can fall back to the bundled config.json values.
    if source_dir is None:
        raise ConfigValidationError(
            'source_dir is required but was not found in any config layer.\n'
            'Provide it via:\n'
            '  • the default data/config.json  ("source_dir" key)\n'
            '  • a custom --config file         ("source_dir" key)\n'
            '  • a positional CLI argument      (python -m organizer /path/to/dir)\n'
            '  • a GUI source-directory widget'
        )

    # ── Construct the final AppConfig ─────────────────────────────────────
    # AppConfig.__init__ will validate that every Path is absolute, so we do
    # not duplicate those checks here.
    return AppConfig(
        source_dir=source_dir,
        dest_dir=dest_dir,
        dry_run=dry_run,
        recursive=recursive,
        ignore_patterns=base_config.ignore_patterns,  # no per-field override yet
        rules_file=rules_file,
        styles_file=styles_file,
        logging=logging_cfg,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Step 2 — Wire all dependencies (Dependency Injection) and run the app
# ─────────────────────────────────────────────────────────────────────────────


def bootstrap(overrides: ConfigOverrides) -> None:
    """
    Composition Root: build every dependency and launch the application.

    This is the ONLY function in the codebase that instantiates infrastructure
    adapters.  Use cases and domain objects never import infrastructure — they
    receive ready-made objects through port (abstract) interfaces.

    Dependency Injection order:
        1.  Merge config layers          → AppConfig
        2.  Wrap AppConfig               → InMemoryConfigRepository  (port: ConfigRepository)
        3.  Pick rules adapter           → JsonRuleRepository         (port: RuleRepository)
        4.  Pick styles adapter          → JsonStyleRepository        (port: StyleRepository)
        5.  Build StyleSet + Logger      → LoguruLogger               (port: Logger)
        6.  Build file system adapter    → OSFileSystem               (port: FileSystem)
        7.  TODO: create and run use case

    Args:
        overrides: Neutral data container from any entry point (CLI, GUI, test).
                   bootstrap() does not know and does not care which one produced it.
    """

    # ── 1. Final merged config ────────────────────────────────────────────
    config: AppConfig = _build_config(overrides)

    # ── 2. Config repository ──────────────────────────────────────────────
    # Why wrap AppConfig in InMemoryConfigRepository?
    #
    # Use cases depend on the ConfigRepository PORT (abstract class), not on
    # AppConfig directly.  This way a use case can be tested by passing any
    # ConfigRepository implementation — including one backed by a test dict —
    # without touching the real JSON files or the CLI.
    #
    #   use case sees:   ConfigRepository          (abstract port)
    #   actual object:   InMemoryConfigRepository  (concrete adapter, holds AppConfig)
    config_repo = InMemoryConfigRepository(config)

    # ── 3. Rules repository ───────────────────────────────────────────────
    # config.rules_file is already resolved (absolute) by _build_config().
    # If it is None (neither config layers nor overrides provided one),
    # fall back to the default rules bundled with the package.
    rules_path = config.rules_file or _DEFAULT_RULES_PATH
    rule_repo = JsonRuleRepository(rules_path)

    # ── 4. Styles repository ──────────────────────────────────────────────
    # Same fallback pattern as rules.
    # The StyleSet produced here drives both logger formatting AND, in the
    # future, the GUI's live style-preview panel.
    styles_path = config.styles_file or _DEFAULT_STYLES_PATH
    style_repo = JsonStyleRepository(styles_path)

    # ── 5. Logger ─────────────────────────────────────────────────────────
    # LoguruLogger needs:
    #   • style_set   — controls colours, icons, and format per log level
    #   • logging_cfg — controls which handlers are active and at what level
    #
    # config.logging is already fully merged by _build_config():
    #   JSON base  +  --log-file patch  OR  full GUI logging dict override
    #
    # The fallback below only fires if config.logging is None (edge case where
    # all config layers had no logging section at all).
    style_set = style_repo.load_styles()
    logging_cfg = config.logging or {'console': {'enabled': True, 'level': 'INFO'}}
    logger = LoguruLogger(logging_cfg, style_set)

    # ── 6. File system adapter ────────────────────────────────────────────
    # OSFileSystem wraps the real operating system.  It has no constructor
    # arguments because all its behaviour comes from the FileSystem port
    # interface that it implements.
    # In tests you would substitute a MockFileSystem instead.
    fs = OSFileSystem()

    # ── 7. TODO: use case ─────────────────────────────────────────────────
    # When OrganizeFilesUseCase is ready, replace the log lines below with:
    #
    #   use_case = OrganizeFilesUseCase(
    #       file_system  = fs,
    #       rule_repo    = rule_repo,
    #       config_repo  = config_repo,
    #       logger       = logger,
    #   )
    #   use_case.execute()
    #
    logger.info('File Organizer started')
    logger.info(f'Source   : {config.source_dir}')
    logger.info(f'Dest     : {config.dest_dir}')
    logger.info(f'Dry run  : {config.dry_run}')
    logger.info(f'Recursive: {config.recursive}')
    logger.info('Bootstrap complete — use case not yet implemented.')
