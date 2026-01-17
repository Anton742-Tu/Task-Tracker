# backend/Dockerfile
# Стадия сборки
FROM python:3.12-slim as builder

WORKDIR /app

# Устанавливаем зависимости для сборки
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install poetry

# Копируем зависимости
COPY pyproject.toml poetry.lock* ./

# Устанавливаем зависимости (без dev)
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Стадия продакшена
FROM python:3.12-slim

WORKDIR /app

# Копируем только нужные библиотеки из builder
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Устанавливаем runtime зависимости
RUN apt-get update && apt-get install -y \
    libpq-dev \
    libmagic1 \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Создаем пользователя для безопасности
RUN groupadd -r django && useradd -r -g django django

# Копируем код
COPY . .

# Меняем владельца файлов
RUN chown -R django:django /app

# Переключаемся на непривилегированного пользователя
USER django

# Собираем статические файлы
RUN python manage.py collectstatic --noinput

# Порт
EXPOSE 8000

# Команда запуска
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "config.wsgi:application"]
