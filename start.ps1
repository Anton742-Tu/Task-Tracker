# Запуск проекта
Write-Host "Запуск Task Tracker..." -ForegroundColor Green

cd backend

# Активируем venv если есть
if (Test-Path ".venv") {
    .venv\Scripts\Activate.ps1
}

# Запускаем сервер
python manage.py runserver