param(
    [string]$TestType = "all",
    [switch]$Coverage,
    [switch]$Verbose,
    [string]$Marker
)

Write-Host "=== Task Tracker - Запуск тестов ===" -ForegroundColor Green
Write-Host "Тип: $TestType" -ForegroundColor Cyan
if ($Coverage) { Write-Host "Покрытие: Включено" -ForegroundColor Cyan }
if ($Verbose) { Write-Host "Подробный вывод: Включен" -ForegroundColor Cyan }
if ($Marker) { Write-Host "Маркер: $Marker" -ForegroundColor Cyan }

$pytestArgs = @()

if ($Verbose) {
    $pytestArgs += "-v"
}

if ($Coverage) {
    $pytestArgs += "--cov=.", "--cov-report=html", "--cov-report=term-missing"
}

if ($Marker) {
    $pytestArgs += "-m", "`"$Marker`""
}

switch ($TestType.ToLower()) {
    "all" {
        $pytestArgs += "."
    }
    "auth" {
        $pytestArgs += "api/tests/auth/"
    }
    "files" {
        $pytestArgs += "api/tests/files/"
    }
    "projects" {
        $pytestArgs += "api/tests/projects/"
    }
    "tasks" {
        $pytestArgs += "api/tests/tasks/"
    }
    "models" {
        $pytestArgs += "apps/"
    }
    "integration" {
        $pytestArgs += "api/tests/integration/"
    }
    default {
        $pytestArgs += $TestType
    }
}

Write-Host "`nЗапуск: pytest $($pytestArgs -join ' ')" -ForegroundColor Gray
$startTime = Get-Date

try {
    python -m pytest @pytestArgs
    $exitCode = $LASTEXITCODE
}
catch {
    Write-Host "Ошибка запуска pytest: $_" -ForegroundColor Red
    $exitCode = 1
}

$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host "`n=== Результаты тестирования ===" -ForegroundColor Green
Write-Host "Время выполнения: $($duration.TotalSeconds.ToString('F2')) сек" -ForegroundColor Cyan

if ($exitCode -eq 0) {
    Write-Host "✅ Все тесты пройдены успешно!" -ForegroundColor Green

    if ($Coverage) {
        $coverageFile = "htmlcov\index.html"
        if (Test-Path $coverageFile) {
            Write-Host "Отчет о покрытии: $coverageFile" -ForegroundColor Cyan
            Write-Host "Откройте в браузере: file:///$((Get-Item $coverageFile).FullName)" -ForegroundColor Cyan
        }
    }
} else {
    Write-Host "❌ Некоторые тесты не пройдены" -ForegroundColor Red
}

exit $exitCode