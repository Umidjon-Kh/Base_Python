# organizer — Developer Guide

> This README is for developers who want to understand, extend, or contribute to the codebase.

---

## Architecture

This project follows **Hexagonal Architecture** (also called Ports and Adapters) with DDD-inspired layering.

The core rule: **inner layers know nothing about outer layers.**

```
┌──────────────────────────────────────────────────┐
│                  bootstrap.py                    │  ← knows everything (intentionally)
├──────────────────────────────────────────────────┤
│               interfaces/cli/                    │  ← entry point, fills ConfigOverrides
├──────────────────────────────────────────────────┤
│               infrastructure/                    │  ← knows application + domain
│  (JsonRuleRepository, OSFileSystem, ...)         │
├──────────────────────────────────────────────────┤
│                application/                      │  ← knows only domain
│    (ports, use cases, AppConfig, DTOs)           │
├──────────────────────────────────────────────────┤
│                   domain/                        │  ← knows nothing
│       (FileItem, Directory, RuleSet, ...)        │
└──────────────────────────────────────────────────┘
```

---

## Layer Responsibilities

### `domain/`
Pure business logic. No I/O, no JSON, no filesystem.

- `FileItem` — represents a single file (path, name, size, parent)
- `Directory` — tree node, holds children. `walk_files()` yields all files depth-first. `walk_dirs()` yields directories deepest-first (safe for deletion)
- `RuleSet` — decides which folder a file belongs to
- `Rule` — base class: `ExtensionRule`, `SizeRule`, `CompositeRule`

### `application/`
Orchestrates the domain. Defines **ports** (abstract interfaces) that infrastructure must implement.

- `ports/` — `FileSystem`, `Logger`, `RuleRepository`, `StyleRepository`, `ConfigRepository`
- `use_cases/OrganizeFilesUseCase` — the only place that runs the actual workflow
- `dto/` — `OrganizeRequest` (input), `OrganizeResult` (output, filled incrementally)
- `AppConfig` — merged config, all fields `Optional`

### `infrastructure/`
Concrete implementations of the ports. The only layer that touches disk, JSON, or loguru.

- `OSFileSystem` — real filesystem via `pathlib` + `shutil`
- `JsonRuleRepository` / `InMemoryRuleRepository`
- `JsonStyleRepository` / `InMemoryStyleRepository`
- `JsonConfigRepository` / `InMemoryConfigRepository`
- `LoguruLogger` — loguru adapter with per-level style support

### `bootstrap.py`
The **Composition Root** — the only file that imports from all layers and wires everything together.

Config merging happens here in three layers:
```
Layer 1 (lowest)   data/config.json         built-in defaults
Layer 2            overrides.config_files   user's own config file
Layer 3 (highest)  ConfigOverrides fields   individual CLI/GUI overrides
```

A field from a higher layer only overrides a lower layer if it is not `None`.

### `interfaces/cli/`
Fills `ConfigOverrides` from `argparse` args and calls `bootstrap()`.
Should never contain business logic.

---

## Config Flow

```
CLI args
    │
    ▼
ConfigOverrides          ← neutral DTO between any entry point and bootstrap()
    │
    ▼
_build_config()          ← merges 3 layers into final AppConfig
    │
    ▼
InMemoryConfigRepository ← wraps AppConfig so use case reads through the port
    │
    ▼
OrganizeFilesUseCase     ← loads config + rules, scans files, moves them
    │
    ▼
OrganizeResult           ← returned to CLI for display
```

---

## How to Add a New Rule Type

1. Create a new class in `domain/rules/` inheriting from `Rule`:

```python
class DateRule(Rule):
    def matches(self, file_item: FileItem) -> bool:
        # your logic here
        ...
```

2. Register it in `InMemoryRuleRepository._parse_rule()`:

```python
elif rule_type == 'date':
    return DateRule(...)
```

3. Do the same in `JsonRuleRepository._parse_rule()`.

4. Add test cases in `tests/test_rules.py`.

---

## How to Add a New Entry Point (e.g. GUI)

1. Create `interfaces/gui/main.py`
2. Fill a `ConfigOverrides` object from your widget values
3. Call `bootstrap(overrides)` and handle `OrganizeResult`

`bootstrap()` and `ConfigOverrides` do not change — that is the whole point of the architecture.

---

## Running Tests

```bash
pytest organizer/tests/
```

Test files:
- `test_file_system.py` — `OSFileSystem` scan and move
- `test_rules.py` — rule repositories and `RuleSet` behavior
- `test_styles.py` — style repositories and `StyleSet`
- `test_logger.py` — `LoguruLogger` output and config
- `test_use_case.py` — `OrganizeFilesUseCase` with fake ports (no real disk)
- `test_bootstrap.py` — full end-to-end integration tests

---

## Data Files

`data/` contains built-in defaults shipped with the package:

- `config.json` — default configuration
- `rules.json` — default file organization rules (Images, Videos, Audio, Documents, Code, ...)
- `styles.json` — default log level styles with icons and colors

These are loaded as Layer 1 in `_build_config()`. Users never need to edit them —
they provide their own files via `--config` / `--rules-file` / `--styles-file`.