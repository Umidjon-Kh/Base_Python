# klart

> _From Swedish — "clear", "neat", "in order"_

**klart** is a command-line tool that brings order to your file system.
Drop it on any folder and it will sort your files into clean, organized subfolders
based on fully configurable rules — by extension, size, or any combination of both.

> ⚠️ **Note:** This project was built by a self-taught developer with ~5-6 weeks of Python experience.
> It is a learning project focused on clean architecture and good practices.
> The code may not be perfect — kind feedback and suggestions are always welcome!

---

## Installation

```bash
pip install klart
```

---

## Quick Start

```bash
# See what would happen — no files are moved
klart ~/Downloads --dry-run

# Organize your Downloads folder
klart ~/Downloads

# Move organized files to a separate folder
klart ~/Downloads --dest ~/Sorted

# Process all subdirectories too
klart ~/Downloads --recursive

# Clean up empty folders after organizing
klart ~/Downloads --clean
```

---

## How It Works

klart reads a set of rules and moves each file into the matching folder:

```
Downloads/
├── photo.jpg      →  Downloads/Images/photo.jpg
├── report.pdf     →  Downloads/Documents/report.pdf
├── song.mp3       →  Downloads/Audio/song.mp3
├── archive.zip    →  Downloads/Archives/archive.zip
└── script.py      →  Downloads/Code/script.py
```

Files that don't match any rule go into `Other/` by default.
You can change this behavior in the config.

---

## CLI Reference

```
positional:
  source_dir              Source directory to organize

options:
  -d, --dest DIR          Destination folder for organized files
  --config FILE           Path to custom JSON config file
  -R, --recursive         Process subdirectories recursively
  -n, --dry-run           Simulate without moving files
  -C, --clean             Remove empty directories after organizing
  -r, --rules JSON        Inline rules config as JSON string
  --rules-file FILE       Path to custom rules JSON file
  -cr, --combine-rules    Combine custom rules with built-in defaults
  -s, --styles JSON       Inline styles config as JSON string
  --styles-file FILE      Path to custom styles JSON file
  -cs, --combine-styles   Combine custom styles with built-in defaults
  -cl, --console-level    Console log level (debug/info/warning/error/critical)
  --log-file FILE         Path to save log file
  -fl, --file-level       File log level (debug/info/warning/error/critical)
  --ignore PATTERN        Ignore files matching pattern (e.g. *.log .tmp)
  -v, --version           Show version and exit
```

---

## Configuration

klart works out of the box with sensible defaults.
Every setting can be overridden via CLI or a custom config file.

**Priority (highest wins):**

```
CLI arguments  >  --config file  >  built-in defaults
```

### Config file

```json
{
  "source_dir": null,
  "dest_dir": null,
  "dry_run": false,
  "recursive": false,
  "ignore_patterns": [".tmp", "*.log"],
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

### Custom rules file

```json
{
  "other_behavior": "use_other",
  "ignore_extensions": [".tmp"],
  "ignore_size_more_than": 2147483648,
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
      "folder": "MediumFiles",
      "priority": 50
    }
  ]
}
```

`other_behavior` options:

- `"use_other"` — move unmatched files to `Other/`
- `"ignore"` — skip unmatched files
- `"raise"` — raise an error for unmatched files

---

## License

MIT
