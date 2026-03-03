<!-- ```markdown -->
# File Organizer

A powerful command-line tool and Python library to automatically sort files into folders based on their extensions.  
Define your own rules, use built‑in defaults, and enjoy beautiful logging with Loguru.

## Features

- 📁 **Sort files by extension** – move `.txt` to `Documents`, `.jpg` to `Images`, etc.
- 🧩 **Custom rules** – via Python‑style dictionary or JSON file.
- 🔁 **Recursive processing** – handle subfolders.
- 🧪 **Dry‑run mode** – preview changes without actually moving files.
- 🧹 **Clean empty directories** – remove empty folders after organization.
- ⚙️ **Configuration file** – store all options in a JSON file.
- 🎨 **Beautiful logging** – fully customizable with Loguru; choose from several built‑in styles or create your own.
- 📦 **Usable as a library** – import `organizer` in your own Python scripts.

## Installation

```bash
git clone https://github.com/Umidjon-kh/Base_Python.git
cd Base_Python/refactoring
pip install -e .
After installation the command organizer will be available in your terminal.

Usage
organizer [OPTIONS] SOURCE
Arguments
Argument	Description
SOURCE	Source folder to organize (required)
Options
Option	Description
--dest, -d PATH	Destination root folder (default: source folder)
--recursive, -R	Process subfolders recursively
--dry-run, -n	Simulate without moving files
--clean, -C	Remove empty directories in source after organization
--rules RULES	Custom rules as a Python dict string, e.g. "{'.txt': 'Texts'}"
--rules-file PATH	JSON file containing custom rules
--combine, -c	Combine user rules with built‑in defaults (user rules take precedence)
--config PATH	Path to a JSON configuration file
--log-file PATH	Write logs to a file
--stream-level, -sl LEVEL	Console log level (debug, info, warning, error, critical)
--write-level, -wl LEVEL	File log level (only if --log-file given)
--style STYLE	Log style name (defined in styles file, default: simple)
--version, -V	Show program version
--help, -h	Show this help message
Examples
bash
# Sort files in‑place
organizer ~/Downloads

# Move files to another folder, process subfolders
organizer ~/Downloads --dest ~/Sorted --recursive

# Preview only
organizer ~/Downloads --dry-run

# Custom rules as a dictionary
organizer ~/Downloads --rules "{'.txt': 'Texts', '.py': 'Scripts'}"

# Use a configuration file
organizer ~/Downloads --config my_config.json

# Logging control
organizer ~/Downloads --stream-level debug --log-file app.log
Configuration file
You can store all options in a JSON file and pass it with --config.
Values from the command line override values from the config file.

Example my_config.json:

json
{
    "core_cfg": {
        "dest": "/home/user/Organized",
        "recursive": true,
        "dry_run": false,
        "clean": true
    },
    "rule_cfg": {
        "rules": "{'.txt': 'Texts', '.py': 'Scripts'}",
        "rules_file": null,
        "combine": false
    },
    "logger_cfg": {
        "console": {
            "enabled": true,
            "level": "debug",
            "style": "modern",
            "colorize": true
        },
        "file": {
            "enabled": false
        },
        "styles_data": null,
        "styles_file": null
    }
}
Rule files
Rules are mappings from file extensions to folder names.
The built‑in defaults are loaded from configs/default_rules.json.

Example my_rules.json:

json
{
    ".jpg": "Images",
    ".png": "Images",
    ".txt": "Documents",
    ".pdf": "Documents"
}
Logging styles
Log styles are defined in configs/default_styles.json. You can add your own styles by providing a custom JSON file via --config (in the logger_cfg.styles_file field) or by inlining styles in logger_cfg.styles_data.

Built‑in styles:

minimalistic – only time and message.

simple – level, name, message.

modern – more detailed with function and line.

split – a compact variant.

Using as a library
python
from organizer import runner, Organizer, RuleManager

# If you have argparse arguments
runner(args, config_path=None)

# Or create your own configuration dict
config = {
    'core_cfg': {'source': '/path/to/folder', 'recursive': True},
    'rule_cfg': {'rules': {'.txt': 'Texts'}},
    'logger_cfg': {}
}
rule_mgr = RuleManager(config['rule_cfg'])
org = Organizer(rule_mgr, config['core_cfg'])
org.organize()
Project structure
text
organizer/
├── __init__.py
├── __main__.py
├── configs/               # JSON configuration files
├── src/
│   ├── cli.py             # Command‑line interface
│   ├── core.py            # Core organizing logic
│   ├── runner.py          # Entry point
│   ├── exceptions/        # Custom exceptions
│   ├── managers/          # Config, rule and log managers
│   └── tools/             # Loader, normalizer, packer utilities
License
This project is licensed under the MIT License. See the LICENSE file for details.

Author
Umidjon-Kh
Repository: https://github.com/Umidjon-kh/Base_Python/tree/main/refactoring
```
