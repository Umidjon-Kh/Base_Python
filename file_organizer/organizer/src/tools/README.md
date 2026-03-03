# Tools

Utility classes used by the managers to perform common tasks.

## `Loader`

Loads JSON data from a file. It knows the default paths for configuration, rules and styles.  
If a custom path is provided, it resolves it and checks existence.

**Methods**:
- `load_from_json(which: str, custom_path: str = None) -> Dict`  
  `which` can be `'config'`, `'rules'` or `'styles'`.

**Example**:
```python
from organizer.src.tools import Loader

styles = Loader.load_from_json('styles', custom_path='my_styles.json')
Normalizer
Normalizes configuration values to the expected types. It handles:

Converting boolean strings ('true'/'false') to real booleans

Converting a rule dictionary string (from CLI) into a real dictionary

Validating that keys in the logging configuration are allowed

Ensuring that extensions start with a dot and are lower‑case

Methods:

normalize_all_data(data: Dict) -> Dict – applies normalisation to every section.

boolean_checker(param, value), rule_checker(rules), rules_normalizer(rules), log_param_normalizer(handler, params) – internal helpers.

Example:

python
from organizer.src.tools import Normalizer

raw_config = {...}
normalized = Normalizer.normalize_all_data(raw_config)
Packer
Combines configuration from different sources (CLI arguments, custom config file, default config) into a single dictionary, respecting the priority order (CLI > custom config > default).

Methods:

pack_args(args) -> Dict – builds a configuration dict from an argparse.Namespace object.

pack_custom_cfg(custom_cfg_path) -> Dict – merges a custom JSON file with the default config.

Example:

python
from organizer.src.tools import Packer

merged = Packer.pack_args(args)
All tools are stateless and can be used as singletons.