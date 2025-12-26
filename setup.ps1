Write-Host "⚡ Настройка окружения Task Tracker" -ForegroundColor Cyan

# 1. Активируем venv
Write-Host "`n1. Активация виртуального окружения..." -ForegroundColor Yellow
cd backend
.\.venv\Scripts\Activate.ps1
cd ..

# 2. Устанавливаем pre-commit
Write-Host "`n2. Установка pre-commit..." -ForegroundColor Yellow
pip install pre-commit

# 3. Устанавливаем hooks
Write-Host "`n3. Установка pre-commit hooks..." -ForegroundColor Yellow
pre-commit install

# 4. Проверяем
Write-Host "`n4. Проверка установки..." -ForegroundColor Yellow
pre-commit --version

Write-Host "`n✅ Настройка завершена!" -ForegroundColor Green
Write-Host "Используйте команды:" -ForegroundColor Cyan
Write-Host "  make help        - список команд"
Write-Host "  make lint        - проверка качества кода"
Write-Host "  pre-commit run --all-files - запуск проверок"