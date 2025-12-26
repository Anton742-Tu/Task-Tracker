@echo off
chcp 65001 >nul

echo.
echo === Task Tracker Management ===

if "%1"=="help" (
    echo Available commands:
    echo.
    echo Development:
    echo   install      - Install dependencies
    echo   run         - Start development server
    echo   shell       - Open Django shell
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
    echo   migrate     - Apply migrations
    echo   makemigrations - Create migrations
    echo.
    echo Usage: make ^<command^>
    goto :end
)

if "%1"=="install" (
    echo Installing dependencies...
    cd backend
    pip install -r requirements.txt
    cd ..
    echo Dependencies installed!
    goto :end
)

if "%1"=="run" (
    echo Starting development server...

    echo Checking dependencies...
    cd backend
    python -c "import rest_framework" 2>nul
    if errorlevel 1 (
        echo Installing missing dependencies...
        pip install -r requirements.txt
    )

    python manage.py runserver
    goto :end
)

if "%1"=="test" (
    echo Running tests...
    cd backend
    python -m pytest -v
    goto :end
)

if "%1"=="lint" (
    echo Running code quality checks...
    echo.
    echo 1. Black - formatting...
    black --check backend
    echo.
    echo 2. Isort - imports...
    isort --check-only backend
    echo.
    echo 3. Flake8 - code style...
    flake8 backend
    echo.
    echo Checks completed!
    goto :end
)

if "%1"=="format" (
    echo Formatting code...
    black backend
    isort backend
    echo Formatting completed!
    goto :end
)

if "%1"=="clean" (
    echo Cleaning temporary files...
    rmdir /s /q __pycache__ 2>nul
    del /s /q *.pyc 2>nul
    cd backend && rmdir /s /q __pycache__ 2>nul && cd ..
    cd backend && del /s /q *.pyc 2>nul && cd ..
    echo Cleaning completed!
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
    cd backend
    python manage.py migrate
    echo Migrations applied!
    goto :end
)

if "%1"=="makemigrations" (
    echo Creating migrations...
    cd backend
    python manage.py makemigrations
    echo Migrations created!
    goto :end
)

if "%1"=="shell" (
    echo Opening Django shell...
    cd backend
    python manage.py shell
    goto :end
)

echo Unknown command: %1
echo.
echo Use 'make help' for available commands

:end