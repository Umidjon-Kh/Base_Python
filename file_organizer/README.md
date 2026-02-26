# File Organizer

A command-line tool to automatically sort files into folders based on their extensions.  
Define your own rules or use the built‑in defaults. Perfect for keeping your downloads or any messy folder tidy.

## Features

- 📁 Sorts files by extension into designated folders (e.g., `.txt` → `Documents`, `.jpg` → `Images`)
- 🧩 Custom rules via Python‑style dictionary or JSON file
- 🔁 Recursive folder processing
- 🧪 Dry‑run mode – see what would happen without actually moving files
- 📝 Flexible logging – console output and optional file logging with configurable levels
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
--rule-file PATH	JSON file containing custom rules
--combine, -c	Combine user rules with built‑in defaults (user rules take precedence)
--recursive, -R	Process subfolders recursively
--dry-run, -n	Simulate without moving any files (automatically sets console log level to debug)
--log-file PATH	Write logs to a file
--stream-level, -sl LEVEL	Console log level: debug, info, warning, error, critical (default: info, but debug when --dry-run is used)
--write-level, -wl LEVEL	File log level (only used if --log-file is given, default: debug)
--help	Show this help message and exit
Examples
bash
# Sort files inside ~/Downloads (in‑place) using default rules
organizer ~/Downloads

# Move files to ~/Sorted, process subfolders recursively
organizer ~/Downloads --dest ~/Sorted --recursive

# Dry run – see what would be moved
organizer ~/Downloads --dry-run

# Use a JSON file with custom rules
organizer ~/Downloads --rule-file my_rules.json

# Provide rules directly as a Python dictionary
organizer ~/Downloads --rules "{'.py': 'Scripts', '.md': 'Docs'}"

# Combine custom rules with built‑in defaults
organizer ~/Downloads --rules "{'.txt': 'Texts'}" --combine

# Write logs to a file with detailed console output
organizer ~/Downloads --log-file app.log --stream-level debug

# Console: only warnings and above; file: all messages (debug)
organizer ~/Downloads --log-file app.log --stream-level warning --write-level debug
Rule Files
Rules are mappings from file extensions to folder names.
The built‑in defaults are loaded from config/default_rules.json (if present) or fall back to a hard‑coded set.

JSON format
json
{
    ".jpg": "Images",
    ".png": "Images",
    ".txt": "Documents",
    ".pdf": "Documents"
}
Python dictionary format (for --rules)
bash
--rules "{'.mp3': 'Music', '.wav': 'Music'}"
Note: The dictionary string must be properly quoted so your shell passes it as one argument. Use single quotes around the whole thing and double quotes inside, or vice versa.

Logging
Logging is configured through the --stream-level, --write-level and --log-file options.

Console output respects --stream-level (default info, but automatically switches to debug when --dry-run is used).

File logging (if enabled) uses --write-level (default debug).

All log messages are also sent to the root logger, so you can easily integrate the tool into larger applications.

License
This project is licensed under the MIT License – see the LICENSE file for details.

Author: Your Name
Repository: https://github.com/Umidjon-kh/Base_Python.git/file_organizer
