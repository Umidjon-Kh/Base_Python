---

### Русский

```markdown
# File Organizer

Мощный инструмент командной строки и Python‑библиотека для автоматической сортировки файлов по папкам на основе их расширений.  
Определяйте свои правила, используйте встроенные настройки и наслаждайтесь красивым логированием с Loguru.

## Возможности

- 📁 **Сортировка по расширению** – перемещает `.txt` в `Documents`, `.jpg` в `Images` и т.д.
- 🧩 **Пользовательские правила** – через словарь Python или JSON‑файл.
- 🔁 **Рекурсивная обработка** – обрабатывает вложенные папки.
- 🧪 **Режим примерки (dry‑run)** – показывает, что будет перемещено, без реального перемещения.
- 🧹 **Очистка пустых папок** – удаляет пустые директории после сортировки.
- ⚙️ **Файл конфигурации** – храните все настройки в JSON.
- 🎨 **Красивое логирование** – полностью настраиваемое с Loguru; несколько встроенных стилей и возможность создать свои.
- 📦 **Использование как библиотеки** – импортируйте `organizer` в свои скрипты.

## Установка

```bash
git clone https://github.com/Umidjon-kh/Base_Python.git
cd Base_Python/refactoring
pip install -e .
После установки в терминале станет доступна команда organizer.

Использование
text
organizer [ОПЦИИ] ИСТОЧНИК
Аргументы
Аргумент	Описание
ИСТОЧНИК	Сортируемая папка (обязательно)
Опции
Опция	Описание
--dest, -d ПУТЬ	Корневая папка назначения (по умолчанию – папка источника)
--recursive, -R	Обрабатывать вложенные папки
--dry-run, -n	Только показать действия, без реального перемещения
--clean, -C	Удалить пустые папки в источнике после сортировки
--rules ПРАВИЛА	Пользовательские правила как строка словаря Python, например "{'.txt': 'Texts'}"
--rules-file ПУТЬ	JSON‑файл с правилами
--combine, -c	Объединить пользовательские правила со встроенными (пользовательские имеют приоритет)
--config ПУТЬ	Путь к JSON‑файлу конфигурации
--log-file ПУТЬ	Записывать логи в файл
--stream-level, -sl УРОВЕНЬ	Уровень логирования в консоли (debug, info, warning, error, critical)
--write-level, -wl УРОВЕНЬ	Уровень логирования в файл (только если указан --log-file)
--style СТИЛЬ	Имя стиля логов (определено в файле стилей, по умолчанию simple)
--version, -V	Показать версию программы
--help, -h	Показать это сообщение
Примеры
bash
# Сортировка в той же папке
organizer ~/Downloads

# Перемещение в другую папку с рекурсивной обработкой
organizer ~/Downloads --dest ~/Sorted --recursive

# Только предпросмотр
organizer ~/Downloads --dry-run

# Пользовательские правила через словарь
organizer ~/Downloads --rules "{'.txt': 'Texts', '.py': 'Scripts'}"

# Использование файла конфигурации
organizer ~/Downloads --config my_config.json

# Управление логированием
organizer ~/Downloads --stream-level debug --log-file app.log
Файл конфигурации
Все опции можно сохранить в JSON‑файле и передать с ключом --config.
Значения из командной строки переопределяют значения из файла.

Пример my_config.json:

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
Файлы правил
Правила — это словарь, где ключ — расширение файла, значение — имя папки.
Встроенные правила загружаются из configs/default_rules.json.

Пример my_rules.json:

json
{
    ".jpg": "Images",
    ".png": "Images",
    ".txt": "Documents",
    ".pdf": "Documents"
}
Стили логирования
Стили определяются в configs/default_styles.json. Вы можете добавить свои стили, передав JSON‑файл через --config (поле logger_cfg.styles_file) или встроив стили в logger_cfg.styles_data.

Встроенные стили:

minimalistic – только время и сообщение.

simple – уровень, имя модуля, сообщение.

modern – подробный стиль с функцией и строкой.

split – компактный вариант.

Использование как библиотеки
python
from organizer import runner, Organizer, RuleManager

# Если у вас есть аргументы argparse
runner(args, config_path=None)

# Или создайте свой словарь конфигурации
config = {
    'core_cfg': {'source': '/path/to/folder', 'recursive': True},
    'rule_cfg': {'rules': {'.txt': 'Texts'}},
    'logger_cfg': {}
}
rule_mgr = RuleManager(config['rule_cfg'])
org = Organizer(rule_mgr, config['core_cfg'])
org.organize()
Структура проекта
text
organizer/
├── __init__.py
├── __main__.py
├── configs/               # JSON‑файлы конфигурации
├── src/
│   ├── cli.py             # Интерфейс командной строки
│   ├── core.py            # Основная логика сортировки
│   ├── runner.py          # Точка входа
│   ├── exceptions/        # Пользовательские исключения
│   ├── managers/          # Менеджеры конфигурации, правил и логов
│   └── tools/             # Утилиты загрузки, нормализации и упаковки
Лицензия
Проект распространяется под лицензией MIT. Подробности см. в файле LICENSE.

Автор
Umidjon-Kh
Репозиторий: https://github.com/Umidjon-kh/Base_Python/tree/main/refactoring