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
from .exceptions import ConfigValidationError


# Default config repo file paths
_DEFAULT_CONFIG_PATH: Path = Path(__file__).parent / 'data' / 'config.json'
_DEFAULT_RULES_PATH: Path = Path(__file__).parent / 'data' / 'rules.json'
_DEFAULT_STYLES_PATH: Path = Path(__file__).parent / 'data' / 'styles.json'

# class ConfigOverrides

class ConfigOverrides:
    """
    Neutral DTo between any entry point and bootstrap()
    """
