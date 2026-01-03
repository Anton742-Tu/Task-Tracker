"""
Скрипт для очистки кэша Python и pytest
"""
import os
import shutil
import sys


def clean_python_cache():
    """Очистка кэша Python"""

    print("Очистка кэша Python...")

    deleted_count = 0

    # Рекурсивно ищем и удаляем __pycache__ и .pyc файлы
    for root, dirs, files in os.walk('.'):
        # Пропускаем виртуальное окружение и скрытые папки
        if any(skip in root for skip in ['.venv', 'venv', '.git', '.idea', '__pycache__']):
            continue

        # Удаляем папку __pycache__ если она есть
        if '__pycache__' in dirs:
            dir_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(dir_path)
                print(f"✓ Удалена: {dir_path}")
                deleted_count += 1
            except Exception as e:
                print(f"✗ Ошибка: {dir_path} - {e}")

        # Удаляем .pyc файлы
        for file_name in files:
            if file_name.endswith('.pyc') or file_name.endswith('.pyo'):
                file_path = os.path.join(root, file_name)
                try:
                    os.remove(file_path)
                    print(f"✓ Удален: {file_path}")
                    deleted_count += 1
                except Exception as e:
                    print(f"✗ Ошибка: {file_path} - {e}")

    # Удаляем папки кэша
    cache_dirs = ['.pytest_cache', '.mypy_cache', 'htmlcov', '.coverage', 'coverage.xml']

    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                if os.path.isdir(cache_dir):
                    shutil.rmtree(cache_dir)
                else:
                    os.remove(cache_dir)
                print(f"✓ Удален: {cache_dir}")
                deleted_count += 1
            except Exception as e:
                print(f"✗ Ошибка: {cache_dir} - {e}")

    return deleted_count


def fix_test_filenames():
    """Исправляет имена тестовых файлов для избежания конфликтов"""

    print("\nПроверка имен тестовых файлов...")

    test_files = []
    for root, dirs, files in os.walk('api/tests'):
        for file_name in files:
            if file_name.startswith('test_') and file_name.endswith('.py'):
                test_files.append(os.path.join(root, file_name))

    # Группируем по именам файлов
    from collections import defaultdict
    file_groups = defaultdict(list)

    for file_path in test_files:
        file_name = os.path.basename(file_path)
        file_groups[file_name].append(file_path)

    # Переименовываем файлы с одинаковыми именами
    renamed_count = 0
    for file_name, file_paths in file_groups.items():
        if len(file_paths) > 1:
            print(f"⚠️  Обнаружено {len(file_paths)} файлов с именем {file_name}")

            for i, file_path in enumerate(file_paths):
                dir_name = os.path.basename(os.path.dirname(file_path))
                new_name = f"test_{dir_name}_{file_name[5:]}" if i == 0 else f"test_{dir_name}_{i}_{file_name[5:]}"
                new_path = os.path.join(os.path.dirname(file_path), new_name)

                try:
                    os.rename(file_path, new_path)
                    print(f"  ✓ Переименован: {file_path} -> {new_name}")
                    renamed_count += 1
                except Exception as e:
                    print(f"  ✗ Ошибка переименования {file_path}: {e}")

    return renamed_count


if __name__ == '__main__':
    # Меняем рабочую директорию на папку скрипта
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print("=" * 50)
    print("Очистка и фикс кэша проекта")
    print("=" * 50)

    deleted = clean_python_cache()
    renamed = fix_test_filenames()

    print("=" * 50)
    if deleted > 0:
        print(f"✅ Удалено файлов кэша: {deleted}")
    if renamed > 0:
        print(f"✅ Переименовано тестовых файлов: {renamed}")

    if deleted == 0 and renamed == 0:
        print("ℹ️  Изменений не требуется")

    print("=" * 50)