.PHONY: help install test test-cov lint format clean migrate run

help:
	@echo "Доступные команды:"
	@echo "  install     - Установить зависимости"
	@echo "  test        - Запустить все тесты"
	@echo "  test-cov    - Запустить тесты с покрытием"
	@echo "  test-files  - Запустить тесты для файлового модуля"
	@echo "  test-auth   - Запустить тесты аутентификации"
	@echo "  lint        - Проверить качество кода"
	@echo "  format      - Форматировать код"
	@echo "  clean       - Очистить временные файлы"
	@echo "  migrate     - Применить миграции"
	@echo "  run         - Запустить сервер разработки"

install:
	pip install -r requirements.txt
	pip install pytest pytest-django pytest-cov black flake8

test:
	cd backend && python -m pytest -v

test-cov:
	cd backend && python -m pytest --cov=. --cov-report=html --cov-report=term-missing

test-files:
	cd backend && python -m pytest api/tests/files/ -v

test-auth:
	cd backend && python -m pytest api/tests/auth/ -v

test-projects:
	cd backend && python -m pytest api/tests/projects/ -v

test-tasks:
	cd backend && python -m pytest api/tests/tasks/ -v

lint:
	cd backend && python -m flake8 . --max-line-length=88 --exclude=migrations,.venv

format:
	cd backend && python -m black . --exclude=migrations

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	find . -name ".pytest_cache" -delete
	find . -name "*.log" -delete
	rm -rf backend/htmlcov/
	rm -rf backend/.coverage

migrate:
	cd backend && python manage.py migrate

run:
	cd backend && python manage.py runserver