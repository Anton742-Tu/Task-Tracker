@echo off
chcp 65001 >nul
echo.

rem Автоматически активируем venv если не активирован
where python >nul 2>&1
if errorlevel 1 (
    echo ⚡ Активация виртуального окружения...
    call backend\.venv\Scripts\activate.bat
)

if "%1"=="help" (
    echo 📖 ДОСТУПНЫЕ КОМАНДЫ (из любой папки проекта):
    echo.
    echo 🚀 РАЗРАБОТКА:
    echo   install           - Установить зависимости
    echo   install-dev       - Установить dev зависимости
    echo   run               - Запустить сервер разработки
    echo   shell             - Открыть Django shell
    echo.
    echo 🧪 ТЕСТИРОВАНИЕ:
    echo   test              - Запустить все тесты
    echo   test-cov          - Тесты с покрытием кода
    echo   test-fast         - Быстрые тесты (без медленных)
    echo.
    echo 🎨 КАЧЕСТВО КОДА:
    echo   lint              - Проверить качество кода
    echo   format            - Отформатировать код
    echo   check-quality     - Полная проверка качества
    echo   pre-commit-install - Установить pre-commit
    echo   pre-commit-run    - Запустить pre-commit
    echo.
    echo 🗄️  БАЗА ДАННЫХ:
    echo   db-up             - Запустить БД
    echo   db-down           - Остановить БД
    echo   migrate           - Применить миграции
    echo   makemigrations    - Создать миграции
    echo.
    echo 🧹 УТИЛИТЫ:
    echo   clean             - Очистить временные файлы
    echo   requirements      - Обновить requirements.txt
    echo.
    echo Использование: make ^<команда^>
    exit /b 0
)

rem Определяем корневую директорию
for %%i in ("%~dp0.") do set "ROOT_DIR=%%~fi"
cd /d "%ROOT_DIR%"

if "%1"=="install" (
    echo 📦 Установка зависимостей...
    cd backend && pip install -r requirements.txt && cd ..
    echo ✅ Зависимости установлены!
    exit /b 0
)

if "%1"=="install-dev" (
    echo 🛠️  Установка dev зависимостей...
    cd backend && pip install -r requirements-dev.txt && cd ..
    echo ✅ Dev зависимости установлены!
    exit /b 0
)

if "%1"=="test" (
    echo 🧪 Запуск тестов...
    cd backend && python -m pytest -v && cd ..
    exit /b 0
)

if "%1"=="test-cov" (
    echo 📊 Запуск тестов с покрытием...
    cd backend && python -m pytest --cov=. --cov-report=html --cov-report=term-missing && cd ..
    echo 📁 Отчет покрытия: backend\htmlcov\index.html
    exit /b 0
)

if "%1"=="lint" (
    echo 🔍 ЗАПУСК ПРОВЕРКИ КАЧЕСТВА КОДА...
    echo.

    echo 🎨 1. Black - форматирование...
    black --check backend apps

    echo.
    echo 🔄 2. Isort - сортировка импортов...
    isort --check-only backend apps

    echo.
    echo 📝 3. Flake8 - стиль кода...
    flake8 backend apps

    echo.
    echo 🔤 4. MyPy - типизация...
    mypy backend

    echo.
    echo ✅ ПРОВЕРКА ЗАВЕРШЕНА!
    exit /b 0
)

if "%1"=="format" (
    echo 🎨 Форматирование кода...
    black backend apps
    isort backend apps
    echo ✅ Форматирование завершено!
    exit /b 0
)

if "%1"=="run" (
    echo 🚀 Запуск сервера разработки...
    cd backend && python manage.py runserver && cd ..
    exit /b 0
)

if "%1"=="shell" (
    echo 💻 Открытие Django shell...
    cd backend && python manage.py shell && cd ..
    exit /b 0
)

if "%1"=="db-up" (
    echo 🐘 Запуск контейнеров БД...
    docker-compose up -d postgres redis
    echo ✅ Контейнеры запущены!
    exit /b 0
)

if "%1"=="db-down" (
    echo 🛑 Остановка контейнеров БД...
    docker-compose down
    echo ✅ Контейнеры остановлены!
    exit /b 0
)

if "%1"=="migrate" (
    echo 📝 Применение миграций...
    cd backend && python manage.py migrate && cd ..
    echo ✅ Миграции применены!
    exit /b 0
)

if "%1"=="makemigrations" (
    echo 📄 Создание миграций...
    cd backend && python manage.py makemigrations && cd ..
    echo ✅ Миграции созданы!
    exit /b 0
)

if "%1"=="clean" (
    echo 🧹 Очистка временных файлов...
    rmdir /s /q __pycache__ 2>nul
    del /s /q *.pyc 2>nul
    del /s /q .coverage 2>nul
    rmdir /s /q htmlcov 2>nul
    rmdir /s /q .pytest_cache 2>nul
    rmdir /s /q .mypy_cache 2>nul
    cd backend && rmdir /s /q __pycache__ 2>nul && cd ..
    cd backend && del /s /q *.pyc 2>nul && cd ..
    echo 🧹 Очистка завершена!
    exit /b 0
)

if "%1"=="pre-commit-install" (
    echo 🔧 Установка pre-commit хуков...
    pre-commit install
    echo ✅ Pre-commit установлен!
    exit /b 0
)

if "%1"=="pre-commit-run" (
    echo 🔍 Запуск pre-commit проверок...
    pre-commit run --all-files
    exit /b 0
)

if "%1"=="check-quality" (
    echo 🔍 ПОЛНАЯ ПРОВЕРКА КАЧЕСТВА...
    echo ========================================
    call :run_check "Black" "black --check backend apps"
    call :run_check "Isort" "isort --check-only backend apps"
    call :run_check "Flake8" "flake8 backend apps"
    call :run_check "MyPy" "mypy backend"
    call :run_check "Django Check" "cd backend && python manage.py check && cd .."
    echo ========================================
    echo ✅ ПРОВЕРКА ЗАВЕРШЕНА!
    exit /b 0
)

if "%1"=="requirements" (
    echo 📋 Обновление requirements...
    cd backend && pip freeze > requirements.txt && cd ..
    echo ✅ Requirements обновлены!
    exit /b 0
)

echo ❌ Неизвестная команда: %1
echo.
echo Используйте 'make help' для просмотра команд
exit /b 1

:run_check
echo.
echo 🔍 Проверка: %~1
%~2
if errorlevel 1 (
    echo ❌ %~1: найдены ошибки
) else (
    echo ✅ %~1: проверка пройдена
)
exit /b 0