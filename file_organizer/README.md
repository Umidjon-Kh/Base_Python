# File Organizer

A command-line tool that organizes files into folders based on configurable rules.

> ⚠️ **Note:** This project was built by a self-taught developer with 2 moths of Python experience.
> It is a learning project — the goal was to practice clean architecture, not to build a production tool.
> Code reviews, suggestions, and kind feedback are very welcome!

---

## Features

- Organize files by extension, size, or composite rules
- Dry-run mode — preview what would happen without moving anything
- Recursive mode — process subdirectories
- Clean mode — remove empty directories after organizing
- Custom rules and styles via JSON config files
- Fully configurable logging (console + file)

---

## Installation

```bash
git clone https://github.com/your-username/file-organizer.git
cd file-organizer
pip install -e .
```

---

## Usage

```bash
# Basic usage
organizer ~/Downloads

# Move organized files to a separate folder
organizer ~/Downloads --dest ~/Sorted

# Preview without moving anything
organizer ~/Downloads --dry-run

# Process subdirectories
organizer ~/Downloads --recursive

# Remove empty folders after organizing
organizer ~/Downloads --clean

# Use a custom rules file
organizer ~/Downloads --rules-file my_rules.json

# Combine custom rules with built-in defaults
organizer ~/Downloads --rules-file my_rules.json --combine-rules

# Use a custom config file
organizer ~/Downloads --config my_config.json
```

---

## Configuration

By default, the organizer uses built-in config from `organizer/data/config.json`.
You can override any setting with CLI arguments or a custom config file.

**Config priority (highest wins):**
```
CLI arguments > --config file > built-in defaults
```

### Config file structure

```json
{
    "source_dir": null,
    "dest_dir": null,
    "dry_run": false,
    "recursive": false,
    "ignore_patterns": [".tmp", "*.log", "*.bak"],
    "rules": {
        "rules_cfg": null,
        "rules_repo": null,
        "combine": false
    },
    "styles": {
        "styles": null,
        "styles_repo": null,
        "combine": false
    },
    "logging": {
        "console": { "enabled": true, "level": "INFO" },
        "file": { "enabled": false, "level": "DEBUG", "path": null }
    }
}
```

### Rules file structure

```json
{
    "other_behavior": "use_other",
    "ignore_extensions": [".tmp", ".log"],
    "ignore_size_more_than": 104857600,
    "ignore_size_less_than": null,
    "rules": [
        {
            "type": "extension",
            "extensions": [".jpg", ".png", ".gif"],
            "folder": "Images",
            "priority": 0
        },
        {
            "type": "size",
            "min": 1048576,
            "max": 104857600,
            "folder": "LargeFiles",
            "priority": 50
        }
    ]
}
```

`other_behavior` options:
- `"use_other"` — move unmatched files to an `Other/` folder
- `"ignore"` — skip unmatched files
- `"raise"` — raise an error for unmatched files

---

## CLI Reference

```
positional:
  source_dir            Source directory to organize

options:
  -d, --dest DIR        Destination folder for organized files
  --config FILE         Path to custom JSON config file
  -R, --recursive       Process subdirectories recursively
  -n, --dry-run         Simulate without moving files
  -C, --clean           Remove empty directories after organizing
  -r, --rules JSON      Inline rules config as JSON string
  --rules-file FILE     Path to custom rules JSON file
  -cr, --combine-rules  Combine custom rules with built-in defaults
  -s, --styles JSON     Inline styles config as JSON string
  --styles-file FILE    Path to custom styles JSON file
  -cs, --combine-styles Combine custom styles with built-in defaults
  -cl, --console-level  Console log level (debug/info/warning/error/critical)
  --log-file FILE       Path to save log file
  -fl, --file-level     File log level (debug/info/warning/error/critical)
  -v, --version         Show version and exit
```

---

## Project Structure

```
file_organizer/
├── organizer/
│   ├── domain/          # Core business entities and rules
│   ├── application/     # Use cases and ports (interfaces)
│   ├── infrastructure/  # Concrete adapters (filesystem, JSON, logging)
│   ├── interfaces/
│   │   └── cli/         # Command-line interface
│   ├── data/            # Built-in default config, rules, styles
│   └── bootstrap.py     # Composition root — wires everything together
└── tests/               # Test suite
```

---

## License

MIT