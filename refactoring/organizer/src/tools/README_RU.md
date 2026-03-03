# Инструменты

Вспомогательные классы, используемые менеджерами для выполнения общих задач.

## `Loader`

Загружает JSON‑данные из файла. Знает пути по умолчанию для конфигурации, правил и стилей.  
Если передан пользовательский путь, разрешает его и проверяет существование.

**Методы**:
- `load_from_json(which: str, custom_path: str = None) -> Dict`  
  `which` может быть `'config'`, `'rules'` или `'styles'`.

**Пример**:
```python
from organizer.src.tools import Loader

styles = Loader.load_from_json('styles', custom_path='my_styles.json')
Normalizer
Приводит значения конфигурации к ожидаемым типам. Умеет:

Преобразовывать строки 'true'/'false' в булевы значения

Преобразовывать строку словаря правил (из CLI) в настоящий словарь

Проверять, что ключи в конфигурации логирования допустимы

Приводить расширения к нижнему регистру и добавлять точку, если её нет

Методы:

normalize_all_data(data: Dict) -> Dict – применяет нормализацию ко всем секциям.

boolean_checker(param, value), rule_checker(rules), rules_normalizer(rules), log_param_normalizer(handler, params) – внутренние помощники.

Пример:

python
from organizer.src.tools import Normalizer

raw_config = {...}
normalized = Normalizer.normalize_all_data(raw_config)
Packer
Объединяет конфигурацию из разных источников (аргументы CLI, пользовательский файл, конфигурация по умолчанию) в единый словарь, соблюдая приоритет (CLI > пользовательский файл > умолчания).

Методы:

pack_args(args) -> Dict – строит словарь конфигурации из объекта argparse.Namespace.

pack_custom_cfg(custom_cfg_path) -> Dict – объединяет пользовательский JSON‑файл с конфигурацией по умолчанию.

Пример:

python
from organizer.src.tools import Packer

merged = Packer.pack_args(args)
Все инструменты не имеют состояния и могут использоваться как синглтоны.