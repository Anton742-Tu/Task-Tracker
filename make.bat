@echo off
chcp 65001 >nul

set BACKEND_DIR=backend
set VENV_DIR=%BACKEND_DIR%\.venv
set PYTHON_EXE=%VENV_DIR%\Scripts\python.exe
set POETRY_EXE=poetry

echo.
echo === Task Tracker Management ===

if "%1"=="help" (
    echo Available commands:
    echo.
    echo Development:
    echo   install      - Install dependencies
    echo   run         - Start development server
    echo   shell       - Open Django shell
    echo   makemigrations - Create migrations
    echo   migrate     - Apply migrations
    echo.
    echo Testing:
    echo   test        - Run tests
    echo   test-cov    - Tests with coverage
    echo.
    echo Code quality:
    echo   lint        - Check code quality
    echo   format      - Format code
    echo   clean       - Clean temporary files
    echo.
    echo Database:
    echo   db-up       - Start database containers
    echo   db-down     - Stop database containers
    echo.
    echo Usage: make ^<command^>
    goto :end
)

if "%1"=="install" (
    echo Installing dependencies...
    cd %BACKEND_DIR%
    %PYTHON_EXE% -m pip install poetry
    %POETRY_EXE% install
    echo Dependencies installed!
    cd ..
    goto :end
)

if "%1"=="run" (
    echo Starting development server...

    REM Проверяем существует ли виртуальное окружение
    if not exist "%VENV_DIR%" (
        echo Virtual environment not found! Creating...
        cd %BACKEND_DIR%
        python -m venv .venv
        .venv\Scripts\python.exe -m pip install --upgrade pip
        .venv\Scripts\python.exe -m pip install poetry
        .venv\Scripts\poetry.exe install
        cd ..
    )

    echo Running server from %BACKEND_DIR%...
    cd %BACKEND_DIR%
    .venv\Scripts\python.exe manage.py runserver
    cd ..
    goto :end
)

if "%1"=="test" (
    echo Running tests...
    cd %BACKEND_DIR%
    .venv\Scripts\python.exe -m pytest -v
    cd ..
    goto :end
)

if "%1"=="test-cov" (
    echo Running tests with coverage...
    cd %BACKEND_DIR%
    .venv\Scripts\python.exe -m pytest --cov=. --cov-report=term-missing --cov-report=html
    echo Coverage report generated in htmlcov/
    cd ..
    goto :end
)

if "%1"=="lint" (
    echo Running code quality checks...
    cd %BACKEND_DIR%
    echo.
    echo 1. Black - formatting...
    .venv\Scripts\python.exe -m black --check .
    echo.
    echo 2. Isort - imports...
    .venv\Scripts\python.exe -m isort --check-only .
    echo.
    echo 3. Flake8 - code style...
    .venv\Scripts\python.exe -m flake8 .
    echo.
    echo Checks completed!
    cd ..
    goto :end
)

if "%1"=="format" (
    echo Formatting code...
    cd %BACKEND_DIR%
    .venv\Scripts\python.exe -m black .
    .venv\Scripts\python.exe -m isort .
    echo Formatting completed!
    cd ..
    goto :end
)

if "%1"=="clean" (
    echo Cleaning temporary files...
    cd %BACKEND_DIR%
    rmdir /s /q __pycache__ 2>nul
    del /s /q *.pyc 2>nul
    del /s /q *.pyo 2>nul
    rmdir /s /q .pytest_cache 2>nul
    rmdir /s /q htmlcov 2>nul
    rmdir /s /q .coverage 2>nul
    rmdir /s /q .mypy_cache 2>nul
    echo Cleaning completed!
    cd ..
    goto :end
)

if "%1"=="db-up" (
    echo Starting database containers...
    docker-compose up -d postgres
    echo Containers started!
    goto :end
)

if "%1"=="db-down" (
    echo Stopping database containers...
    docker-compose down
    echo Containers stopped!
    goto :end
)

if "%1"=="migrate" (
    echo Applying migrations...
    cd %BACKEND_DIR%
    .venv\Scripts\python.exe manage.py migrate
    echo Migrations applied!
    cd ..
    goto :end
)

if "%1"=="makemigrations" (
    echo Creating migrations...
    cd %BACKEND_DIR%
    .venv\Scripts\python.exe manage.py makemigrations
    echo Migrations created!
    cd ..
    goto :end
)

if "%1"=="shell" (
    echo Opening Django shell...
    cd %BACKEND_DIR%
    .venv\Scripts\python.exe manage.py shell
    cd ..
    goto :end
)

if "%1"=="venv-activate" (
    echo Activating virtual environment...
    echo Run: %BACKEND_DIR%\.venv\Scripts\Activate
    goto :end
)

if "%1"=="venv-setup" (
    echo Setting up virtual environment...
    cd %BACKEND_DIR%
    echo 1. Creating virtual environment...
    python -m venv .venv
    echo 2. Upgrading pip...
    .venv\Scripts\python.exe -m pip install --upgrade pip
    echo 3. Installing Poetry...
    .venv\Scripts\python.exe -m pip install poetry
    echo 4. Installing dependencies...
    .venv\Scripts\python.exe -m poetry install
    echo Setup completed!
    cd ..
    goto :end
)

echo Unknown command: %1
echo.
echo Use 'make help' for available commands

if "%1"=="collectstatic" (
    echo Collecting static files...
    cd %BACKEND_DIR%
    .venv\Scripts\python.exe manage.py collectstatic --noinput
    echo Static files collected!
    cd ..
    goto :end
)

if "%1"=="static" (
    echo Setting up static files...
    mkdir %BACKEND_DIR%\static 2>nul
    mkdir %BACKEND_DIR%\static\css 2>nul
    mkdir %BACKEND_DIR%\static\js 2>nul
    mkdir %BACKEND_DIR%\static\images 2>nul
    mkdir %BACKEND_DIR%\media 2>nul
    echo Static directories created!
    goto :end
)

:end