FROM python:3.12-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry==1.7.0 && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction

# Копируем код
COPY backend/ ./backend/

# Рабочая директория для Django
WORKDIR /app/backend

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]