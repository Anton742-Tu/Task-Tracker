"""
Настройки для локальной разработки
"""

import os
from .base import *  # Не волнуемся о F403, это нужно для Django

# Debug mode
DEBUG = True

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

# Debug toolbar
INSTALLED_APPS += [  # type: ignore  # Игнорируем mypy предупреждение
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
LOGGING["loggers"]["django"]["level"] = "DEBUG"  # type: ignore
LOGGING["handlers"]["console"]["level"] = "DEBUG"  # type: ignore

# Выводим информацию о настройках
print("=" * 50)
print("🚀 РАЗРАБОТКА: DEBUG MODE ENABLED")
print(f"📁 Database: {DATABASES['default']['ENGINE']}")
print(f"🌐 Allowed hosts: {ALLOWED_HOSTS}")
print("=" * 50)
