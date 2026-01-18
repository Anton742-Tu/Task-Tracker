# Используй FROM и AS с одинаковым регистром
FROM python:3.12-slim AS builder

WORKDIR /app

# Устанавливаем зависимости для сборки
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Копируем backend и зависимости
COPY backend/requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Стадия продакшена
FROM python:3.12-slim

WORKDIR /app

# Копируем зависимости из builder
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

# Копируем backend код
COPY backend/ .

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
