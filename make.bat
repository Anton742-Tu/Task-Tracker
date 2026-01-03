@echo off
chcp 65001 >nul

set BACKEND_DIR=backend
set VENV_DIR=%BACKEND_DIR%\.venv
set PYTHON_EXE=%VENV_DIR%\Scripts\python.exe

echo.
echo === Task Tracker Management ===

if "%1"=="" (
    echo.
    echo Установка и настройка:
    echo   make install      - Установить зависимости через Poetry
    echo   make venv         - Создать виртуальное окружение
    echo.
    echo Разработка:
    echo   make run          - Запустить сервер разработки
    echo   make shell        - Открыть Django shell
    echo   make admin        - Создать суперпользователя
    echo.
    echo База данных:
    echo   make db-up        - Запустить БД в Docker
    echo   make db-down      - Остановить БД в Docker
    echo   make migrate      - Применить миграции
    echo   make makemigrations - Создать миграции
    echo.
    echo Тестирование:
    echo   make test         - Запустить все тесты
    echo   make test-cov     - Тесты с отчетом о покрытии
    echo.
    echo Качество кода:
    echo   make lint         - Проверить код (flake8, black, isort)
    echo   make format       - Форматировать код (black, isort)
    echo.
    echo Утилиты:
    echo   make clean        - Очистить временные файлы
    echo   make collectstatic - Собрать статические файлы
    echo   make static       - Создать папки для статики
    echo   make create-users - Создать тестовых пользователей
    echo.
    echo Использование: make ^<команда^>
    goto :end
)

if "%1"=="install" (
    echo Установка зависимостей...
    if not exist "%VENV_DIR%" (
        echo Создание виртуального окружения...
        cd %BACKEND_DIR%
        python -m venv .venv
        cd ..
    )
    cd %BACKEND_DIR%
    call .venv\Scripts\activate.bat
    pip install poetry
    poetry install
    echo ✅ Зависимости установлены
    goto :end
)

if "%1"=="run" (
    echo Запуск сервера разработки...
    if not exist "%PYTHON_EXE%" (
        echo Ошибка: Виртуальное окружение не найдено!
        echo Запустите сначала: make install
        goto :end
    )
    cd %BACKEND_DIR%
    %PYTHON_EXE% manage.py runserver
    goto :end
)

if "%1"=="migrate" (
    echo Применение миграций...
    if not exist "%PYTHON_EXE%" (
        echo Ошибка: Виртуальное окружение не найдено!
        echo Запустите сначала: make install
        goto :end
    )
    cd %BACKEND_DIR%
    %PYTHON_EXE% manage.py migrate
    echo ✅ Миграции применены
    goto :end
)

if "%1"=="makemigrations" (
    echo Создание миграций...
    if not exist "%PYTHON_EXE%" (
        echo Ошибка: Виртуальное окружение не найдено!
        echo Запустите сначала: make install
        goto :end
    )
    cd %BACKEND_DIR%
    %PYTHON_EXE% manage.py makemigrations
    echo ✅ Миграции созданы
    goto :end
)

if "%1"=="test" (
    echo Запуск тестов...
    if not exist "%PYTHON_EXE%" (
        echo Ошибка: Виртуальное окружение не найдено!
        echo Запустите сначала: make install
        goto :end
    )
    cd %BACKEND_DIR%
    %PYTHON_EXE% -m pytest -v
    goto :end
)

if "%1"=="lint" (
    echo Проверка качества кода...
    if not exist "%PYTHON_EXE%" (
        echo Ошибка: Виртуальное окружение не найдено!
        echo Запустите сначала: make install
        goto :end
    )
    cd %BACKEND_DIR%
    echo.
    echo 1. Проверка стиля (flake8)...
    %PYTHON_EXE% -m flake8 .
    echo.
    echo 2. Проверка форматирования (black)...
    %PYTHON_EXE% -m black --check .
    echo.
    echo 3. Проверка импортов (isort)...
    %PYTHON_EXE% -m isort --check-only .
    echo.
    echo ✅ Проверка завершена
    goto :end
)

if "%1"=="format" (
    echo Форматирование кода...
    if not exist "%PYTHON_EXE%" (
        echo Ошибка: Виртуальное окружение не найдено!
        echo Запустите сначала: make install
        goto :end
    )
    cd %BACKEND_DIR%
    %PYTHON_EXE% -m black .
    %PYTHON_EXE% -m isort .
    echo ✅ Код отформатирован
    goto :end
)

if "%1"=="clean" (
    echo Очистка временных файлов...
    cd %BACKEND_DIR%
    rmdir /s /q __pycache__ 2>nul
    del /s /q *.pyc 2>nul
    del /s /q *.pyo 2>nul
    rmdir /s /q .pytest_cache 2>nul
    rmdir /s /q htmlcov 2>nul
    del /s /q .coverage 2>nul
    rmdir /s /q .mypy_cache 2>nul
    echo ✅ Временные файлы удалены
    goto :end
)

if "%1"=="collectstatic" (
    echo Сбор статических файлов...
    if not exist "%PYTHON_EXE%" (
        echo Ошибка: Виртуальное окружение не найдено!
        echo Запустите сначала: make install
        goto :end
    )
    cd %BACKEND_DIR%
    %PYTHON_EXE% manage.py collectstatic --noinput
    echo ✅ Статические файлы собраны
    goto :end
)

if "%1"=="static" (
    echo Создание папок для статики...
    mkdir %BACKEND_DIR%\static 2>nul
    mkdir %BACKEND_DIR%\static\css 2>nul
    mkdir %BACKEND_DIR%\static\js 2>nul
    mkdir %BACKEND_DIR%\static\images 2>nul
    mkdir %BACKEND_DIR%\media 2>nul
    mkdir %BACKEND_DIR%\media\uploads 2>nul
    mkdir %BACKEND_DIR%\staticfiles 2>nul
    echo ✅ Папки созданы
    goto :end
)

if "%1"=="shell" (
    echo Открытие Django shell...
    if not exist "%PYTHON_EXE%" (
        echo Ошибка: Виртуальное окружение не найдено!
        echo Запустите сначала: make install
        goto :end
    )
    cd %BACKEND_DIR%
    %PYTHON_EXE% manage.py shell
    goto :end
)

if "%1"=="admin" (
    echo Создание суперпользователя...
    if not exist "%PYTHON_EXE%" (
        echo Ошибка: Виртуальное окружение не найдено!
        echo Запустите сначала: make install
        goto :end
    )
    cd %BACKEND_DIR%
    %PYTHON_EXE% manage.py createsuperuser
    goto :end
)

if "%1"=="db-up" (
    echo Запуск базы данных в Docker...
    docker-compose up -d postgres
    echo ✅ База данных запущена
    echo    PostgreSQL: localhost:5432
    echo    pgAdmin: http://localhost:5050 (admin@admin.com/admin)
    goto :end
)

if "%1"=="db-down" (
    echo Остановка базы данных...
    docker-compose down
    echo ✅ База данных остановлена
    goto :end
)

if "%1"=="create-users" (
    echo Создание тестовых пользователей...
    if not exist "%PYTHON_EXE%" (
        echo Ошибка: Виртуальное окружение не найдено!
        echo Запустите сначала: make install
        goto :end
    )
    cd %BACKEND_DIR%
    %PYTHON_EXE% -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
users = [
    ('admin', 'admin123', 'Админ', True, True),
    ('manager', 'manager123', 'Менеджер', False, False),
    ('employee', 'employee123', 'Сотрудник', False, False),
]
for username, password, role, is_staff, is_super in users:
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(username=username, password=password)
        user.role = role.lower()
        user.is_staff = is_staff
        user.is_superuser = is_super
        user.save()
        print(f'✅ Создан: {username}/{password} ({role})')
    else:
        print(f'⚠️  Уже существует: {username}')
"
    goto :end
)

echo Неизвестная команда: %1
echo.
echo Используйте 'make' без аргументов для списка команд

:end