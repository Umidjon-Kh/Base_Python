from pathlib import Path
from infrastructure.file_system.os_file_system import OSFileSystem

fs = OSFileSystem()
root = fs.scan(Path('/home/umidjon/Documents/Base_Python/refactoring'))  # укажи реальный путь

print(root.name)
for file in root.walk_files():
    print(file.info())
