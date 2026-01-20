"""
Настройки для локальной разработки
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

from .base import *  # Не волнуемся о F403, это нужно для Django
from .debug_toolbar_settings import DEBUG_TOOLBAR_CONFIG

# Загружаем переменные из .env.development
load_dotenv(".env.development")

# Debug mode
DEBUG = os.getenv("DEBUG", "True") == "True"

# Секретный ключ для разработки
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-dev-key-change-in-production")

# Разрешенные хосты
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "task_tracker_dev"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", "postgres"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "ATOMIC_REQUESTS": True,
    }
}

# Email
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Telegram настройки (теперь из .env)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Парсим JSON из переменной TELEGRAM_CHAT_IDS
telegram_chat_ids_str = os.getenv("TELEGRAM_CHAT_IDS", "{}")
try:
    TELEGRAM_CHAT_IDS = json.loads(telegram_chat_ids_str)
except json.JSONDecodeError:
    TELEGRAM_CHAT_IDS = {
        "admin": os.getenv("TELEGRAM_ADMIN_CHAT_ID", ""),
        "executor": os.getenv("TELEGRAM_EXECUTOR_CHAT_ID", ""),
    }

SITE_URL = os.getenv("SITE_URL", "http://localhost:8000")

# Debug toolbar
INSTALLED_APPS += [  # type: ignore
    "debug_toolbar",
]

# Вставляем в начало списка middleware
debug_toolbar_index = 0
if "debug_toolbar.middleware.DebugToolbarMiddleware" not in MIDDLEWARE:  # type: ignore
    MIDDLEWARE.insert(debug_toolbar_index, "debug_toolbar.middleware.DebugToolbarMiddleware")  # type: ignore

INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

# CORS для разработки
CORS_ALLOWED_ORIGINS += [  # type: ignore
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Разрешаем все для разработки
CORS_ALLOW_ALL_ORIGINS = True

# DRF разрешает все в разработке
REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = [  # type: ignore
    "rest_framework.permissions.AllowAny",
]

# Логирование более детальное в разработке
LOGGING["loggers"]["django"]["level"] = "WARNING"  # type: ignore
LOGGING["handlers"]["console"]["level"] = "INFO"  # type: ignore

# Выводим информацию о настройках
print("=" * 50)
print("🚀 РАЗРАБОТКА: DEBUG MODE ENABLED")
print(f"📁 Database: {DATABASES['default']['ENGINE']}")
print(f"🤖 Telegram Bot: {'✅ Настроен' if TELEGRAM_BOT_TOKEN else '❌ Не настроен'}")
print(f"👤 Telegram Users: {len(TELEGRAM_CHAT_IDS)}")
print(f"🌐 Site URL: {SITE_URL}")
print("=" * 50)
