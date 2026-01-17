# Настройка проекта
Write-Host "Настройка Task Tracker..." -ForegroundColor Green

# Создаем .env если нет
if (-not (Test-Path "backend/.env")) {
    Copy-Item "backend/.env.example" "backend/.env"
    Write-Host "Создан .env файл" -ForegroundColor Yellow
}

Write-Host "Готово! Запустите: .\start.ps1" -ForegroundColor Green