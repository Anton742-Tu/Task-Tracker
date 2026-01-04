.PHONY: help install test test-cov test-auth test-files test-projects test-tasks test-models lint format clean migrate run

help:
	@echo "=== Task Tracker Management ==="
	@echo ""
	@echo "Установка и настройка:"
	@echo "  make install      - Установить зависимости"
	@echo ""
	@echo "Разработка:"
	@echo "  make run          - Запустить сервер разработки"
	@echo "  make shell        - Открыть Django shell"
	@echo "  make admin        - Создать суперпользователя"
	@echo ""
	@echo "База данных:"
	@echo "  make migrate      - Применить миграции"
	@echo "  make makemigrations - Создать миграции"
	@echo ""
	@echo "Тестирование:"
	@echo "  make test         - Запустить все тесты"
	@echo "  make test-cov     - Тесты с отчетом о покрытии"
	@echo "  make test-auth    - Тесты аутентификации"
	@echo "  make test-files   - Тесты файлового модуля"
	@echo "  make test-projects - Тесты проектов"
	@echo "  make test-tasks   - Тесты задач"
	@echo "  make test-models  - Тесты моделей приложений"
	@echo ""
	@echo "Качество кода:"
	@echo "  make lint         - Проверить код (flake8, black, isort)"
	@echo "  make format       - Форматировать код (black, isort)"
	@echo ""
	@echo "Утилиты:"
	@echo "  make clean        - Очистить временные файлы"
	@echo "  make collectstatic - Собрать статические файлы"
	@echo ""

install:
	cd backend && pip install -r requirements.txt
	cd backend && pip install pytest pytest-django pytest-cov black flake8 isort

run:
	cd backend && python manage.py runserver

shell:
	cd backend && python manage.py shell

admin:
	cd backend && python manage.py createsuperuser

migrate:
	cd backend && python manage.py migrate

makemigrations:
	cd backend && python manage.py makemigrations

test:
	cd backend && python -m pytest -v

test-cov:
	cd backend && python -m pytest --cov=. --cov-report=html --cov-report=term-missing
	@echo ""
	@echo "Отчет о покрытии: backend/htmlcov/index.html"

test-auth:
	cd backend && python -m pytest api/tests/auth/ -v

test-files:
	cd backend && python -m pytest api/tests/files/ -v

test-projects:
	cd backend && python -m pytest api/tests/projects/ -v

test-tasks:
	cd backend && python -m pytest api/tests/tasks/ -v

test-models:
	cd backend && python -m pytest apps/ -v

lint:
	cd backend && python -m flake8 . --max-line-length=88 --exclude=migrations,.venv
	cd backend && python -m black --check . --exclude=migrations
	cd backend && python -m isort --check-only . --skip-glob=migrations

format:
	cd backend && python -m black . --exclude=migrations
	cd backend && python -m isort . --skip-glob=migrations

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	find . -name ".pytest_cache" -delete
	find . -name "*.log" -delete
	rm -rf backend/htmlcov/
	rm -rf backend/.coverage

collectstatic:
	cd backend && python manage.py collectstatic --noinput