<!-- ```markdown -->
# Менеджеры

В этом каталоге находятся основные менеджеры, управляющие различными аспектами File Organizer.

## `ConfigManager`

Отвечает за загрузку, объединение и нормализацию конфигурации из нескольких источников:
- Аргументы командной строки
- Пользовательский файл конфигурации (JSON)
- Конфигурация по умолчанию (из `configs/default_configs.json`)

Результирующая объединённая конфигурация разделена на три части:
- `core_cfg` – для класса `Organizer`
- `rule_cfg` – для `RuleManager`
- `logger_cfg` – для `LogManager`

**Использование**:
```python
from organizer.src.managers import ConfigManager

config_mgr = ConfigManager(args, custom_cfg_path="my_config.json")
merged_config = config_mgr.configs
RuleManager
Управляет сопоставлением расширений файлов с именами папок. Поддерживает:

Загрузку правил из JSON‑файла

Использование правил, переданных в виде строки словаря Python (из CLI)

Объединение пользовательских правил со встроенными

Использование:

python
from organizer.src.managers import RuleManager

rule_mgr = RuleManager(config={'rules': {'.txt': 'Texts'}, 'combine': True})
folder = rule_mgr.get_folder('.txt')   # вернёт 'Texts'
LogManager
Настраивает логирование Loguru на основе параметров из logger_cfg. Умеет:

Включать/отключать консольный и файловый вывод

Задавать уровни логирования

Выбирать стиль логов (из styles_data)

Настраивать цвета, ротацию, хранение и т.д.

Использование:

python
from organizer.src.managers import LogManager

log_mgr = LogManager(config={
    'console': {'enabled': True, 'level': 'debug', 'style': 'modern'},
    'file': {'enabled': False}
})
# После этого вызова Loguru настроен глобально