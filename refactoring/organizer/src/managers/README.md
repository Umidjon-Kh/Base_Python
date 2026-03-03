<!-- ```markdown -->
# Managers

This directory contains the core managers that handle different aspects of the File Organizer.

## `ConfigManager`

Responsible for loading, merging and normalizing configuration from multiple sources:
- Command‑line arguments
- Custom configuration file (JSON)
- Default configuration (from `configs/default_configs.json`)

The resulting merged configuration is split into three parts:
- `core_cfg` – for the `Organizer` class
- `rule_cfg` – for the `RuleManager`
- `logger_cfg` – for the `LogManager`

**Usage**:
```python
from organizer.src.managers import ConfigManager

config_mgr = ConfigManager(args, custom_cfg_path="my_config.json")
merged_config = config_mgr.configs
RuleManager
Manages the mapping from file extensions to folder names. It supports:

Loading rules from a JSON file

Using rules provided as a Python dictionary string (from CLI)

Combining user rules with built‑in defaults

Usage:

python
from organizer.src.managers import RuleManager

rule_mgr = RuleManager(config={'rules': {'.txt': 'Texts'}, 'combine': True})
folder = rule_mgr.get_folder('.txt')   # returns 'Texts'
LogManager
Configures Loguru logging based on the settings from logger_cfg. It can:

Enable/disable console and file logging

Set log levels

Choose a log style (from styles_data)

Customise colours, rotation, retention, etc.

Usage:

python
from organizer.src.managers import LogManager

log_mgr = LogManager(config={
    'console': {'enabled': True, 'level': 'debug', 'style': 'modern'},
    'file': {'enabled': False}
})
# After this call, Loguru is globally configured