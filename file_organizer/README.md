# File Organizer

A command-line tool to automatically sort files into folders based on their extensions.  
Define your own rules or use the built‑in defaults. Perfect for keeping your downloads or any messy folder tidy.

## Features

- 📁 Sorts files by extension into designated folders (e.g., `.txt` → `Documents`, `.jpg` → `Images`)
- 🧩 Custom rules via Python‑style dictionary or JSON file
- 🔁 Recursive folder processing
- 🧪 Dry‑run mode – see what would happen without actually moving files
- 📝 Flexible logging – console output and optional file logging with configurable levels
- ⚙️ Configuration file support – store all options in a JSON file
- 🔄 Priority: CLI overrides config file, config file overrides defaults
- ⚡ Lightweight, uses only the Python standard library

## Installation

You can install the package directly from the source:

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/Umidjon-kh/Base_Python.git
cd Base_Python/file_organizer

# Install in editable mode (recommended for development)
pip install -e .
After installation the command organizer will be available in your terminal.

Usage
text
organizer [OPTIONS] SOURCE
Arguments
Argument	Description
SOURCE	Source folder to organize (required)
Options
Option	Description
--dest, -d PATH	Destination root folder (default: source folder)
--rules RULES	Custom rules as a Python dictionary string, e.g. "{'.txt': 'Docs'}"
--rules-file PATH	JSON file containing custom rules
--combine, -c	Combine user rules with built‑in defaults (user rules take precedence)
--recursive, -R	Process subfolders recursively
--dry-run, -n	Simulate without moving any files (automatically sets console log level to debug)
--clean-source, -C	Remove empty directories in source after organization
--config PATH	Path to a JSON configuration file (see below for format)
--log-file PATH	Write logs to a file
--stream-level, -sl LEVEL	Console log level: debug, info, warning, error, critical (default: info)
--write-level, -wl LEVEL	File log level (default: debug; only used if --log-file is given)
--version, -V	Show program version and exit
--help, -h	Show this help message and exit
Configuration file
You can store all options in a JSON file and pass it with --config.
The file should contain a JSON object with keys matching the long option names (without leading dashes).
Values from the command line override values from the config file.

Example my_config.json:

json
{
    "dest": "/home/user/Organized",
    "recursive": true,
    "dry_run": false,
    "clean_source": true,
    "rules": "{'.txt': 'Texts', '.py': 'Scripts'}",
    "log_file": "/home/user/organizer.log",
    "stream_level": "debug",
    "write_level": "info"
}
Then run:

bash
organizer ~/Downloads --config my_config.json
Rule files
Rules are mappings from file extensions to folder names.
The built‑in defaults are loaded from organizer/configs/default_rules.json (if present) or fall back to a hard‑coded set.

JSON format (for --rules-file):

json
{
    ".jpg": "Images",
    ".png": "Images",
    ".txt": "Documents",
    ".pdf": "Documents"
}
Python dictionary format (for --rules):

bash
--rules "{'.mp3': 'Music', '.wav': 'Music'}"
Note: The dictionary string must be properly quoted so your shell passes it as one argument. Use single quotes around the whole thing and double quotes inside, or vice versa.

Logging
Console output respects --stream-level (default info).

File logging (if enabled) respects --write-level (default debug).

In dry‑run mode, console level is automatically set to debug to show all planned actions.

All log messages are also sent to the root logger, so you can easily integrate the tool into larger applications.

Priority of settings
Command line arguments – highest priority

Configuration file (if given) – overrides defaults

Built‑in defaults – lowest priority

License
This project is licensed under the MIT License – see the LICENSE file for details.

Author
Umidjon-Kh
Repository: https://github.com/Umidjon-kh/Base_Python/tree/main/file_organizer