import os

import pyperclip

# Задаем флаги
include_content = 1  # True для включения содержимого, False для исключения
use_exclusions = 1  # True для использования исключений, False для их игнорирования

EXCLUDED_FILES = {"README.txt", "requirements.txt", "___struct.py", ".gitignore"}
EXCLUDED_DIRS = {"__pycache__", ".venv", ".git", ".pytest_cache"}


def get_file_structure(start_path, include_content=True, use_exclusions=True):
    file_structure = []

    for root, dirs, files in os.walk(start_path):
        # Игнорируем каталоги, если используется исключение
        if use_exclusions:
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        # Добавляем информацию о папках
        for d in dirs:
            full_dir_path = os.path.join(root, d)  # Полный путь к папке
            relative_dir_path = os.path.relpath(
                full_dir_path, start_path
            )  # Относительный путь
            file_structure.append("/app/" + relative_dir_path + "/")

            if include_content:
                # Проверка, нужно ли собирать содержимое папки
                content = f"# Содержимое папки {d}:\n"
                try:
                    inner_files = os.listdir(full_dir_path)
                    content += (
                        "\n".join(inner_files) if inner_files else "# Папка пуста"
                    )
                except Exception as e:
                    content = f"# Ошибка при получении содержимого папки: {e}"

                file_structure.append(content)

        for f in files:
            if use_exclusions and f in EXCLUDED_FILES:  # Проверяем на исключение
                continue

            full_file_path = os.path.join(root, f)  # Полный путь к файлу
            relative_file_path = os.path.relpath(
                full_file_path, start_path
            )  # Относительный путь
            file_structure.append("/app/" + relative_file_path)

            if include_content:
                # Читаем содержимое файла
                try:
                    with open(full_file_path, "r", encoding="utf-8") as file:
                        content = file.read()
                        if not content:
                            content = "# Это пустой файл"
                        else:
                            content = f"# НАЧАЛО ФАЙЛА\n{content}\n# КОНЕЦ ФАЙЛА"  # Добавляем комментарии
                except Exception as e:
                    content = f"# Ошибка при чтении файла: {e}"

                file_structure.append(content)

    return "\n".join(file_structure)


current_path = os.getcwd()  # Получаем текущее рабочее расположение
structure = get_file_structure(current_path, include_content, use_exclusions)
pyperclip.copy(structure)  # Копируем структуру в буфер обмена
print("Структура файлов и папок с содержимым скопирована в буфер обмена.")
