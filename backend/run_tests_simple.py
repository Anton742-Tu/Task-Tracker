#!/usr/bin/env python
"""
Простой скрипт для запуска тестов
"""
import os
import sys
import subprocess


def run_tests():
    """Запуск тестов Django"""

    print("=" * 50)
    print("Запуск тестов Django проекта")
    print("=" * 50)

    # Устанавливаем настройки
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    # Импортируем Django
    import django
    django.setup()

    # Отключаем Debug Toolbar если он есть
    from django.conf import settings

    if 'debug_toolbar' in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS.remove('debug_toolbar')
        print("✓ Отключен Debug Toolbar")

    if 'debug_toolbar.middleware.DebugToolbarMiddleware' in settings.MIDDLEWARE:
        settings.MIDDLEWARE.remove('debug_toolbar.middleware.DebugToolbarMiddleware')
        print("✓ Удален middleware Debug Toolbar")

    # Запускаем тесты
    print("\nЗапуск тестов...")
    result = subprocess.run([sys.executable, '-m', 'pytest', '-v'])

    print("=" * 50)
    if result.returncode == 0:
        print("✅ Все тесты пройдены успешно!")
    else:
        print("❌ Некоторые тесты не пройдены")
    print("=" * 50)

    return result.returncode


if __name__ == '__main__':
    sys.exit(run_tests())