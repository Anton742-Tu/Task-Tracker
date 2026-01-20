"""
Настройки для продакшена
"""

import os
from .base import *  # type: ignore

# Для продакшена нам нужны дополнительные импорты
try:
    import dj_database_url
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
except ImportError:
    # Если не установлены, это нормально для разработки
    dj_database_url = None  # type: ignore
    sentry_sdk = None  # type: ignore

# Debug mode
DEBUG = False

# Секретный ключ (обязательно из переменных окружения)
SECRET_KEY = os.environ.get("SECRET_KEY", "")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY must be set in production!")

# Разрешенные хосты (обязательно из переменных окружения)
allowed_hosts = os.environ.get("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [h.strip() for h in allowed_hosts.split(",") if h.strip()]
if not ALLOWED_HOSTS:
    raise ValueError("ALLOWED_HOSTS must be set in production!")

# Database
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and dj_database_url:
    DATABASES = {  # type: ignore
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Используем стандартные переменные окружения
    DATABASES = {  # type: ignore
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_NAME", ""),
            "USER": os.environ.get("DB_USER", ""),
            "PASSWORD": os.environ.get("DB_PASSWORD", ""),
            "HOST": os.environ.get("DB_HOST", ""),
            "PORT": os.environ.get("DB_PORT", "5432"),
            "CONN_MAX_AGE": 600,
            "OPTIONS": {
                "sslmode": "require",
            },
        }
    }

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 год
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_REFERRER_POLICY = "same-origin"

# CORS только для доверенных источников
cors_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "")
if cors_origins:
    CORS_ALLOWED_ORIGINS = [o.strip() for o in cors_origins.split(",") if o.strip()]  # type: ignore
CORS_ALLOW_CREDENTIALS = True

# Telegram настройки
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Парсим JSON из переменной TELEGRAM_CHAT_IDS
telegram_chat_ids_str = os.getenv("TELEGRAM_CHAT_IDS", "{}")
try:
    TELEGRAM_CHAT_IDS = json.loads(telegram_chat_ids_str)
except json.JSONDecodeError:
    TELEGRAM_CHAT_IDS = {}

SITE_URL = os.getenv("SITE_URL", "")

# Email настройки
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

# Кэширование (используем Redis если доступен)
REDIS_URL = os.environ.get("REDIS_URL")
if REDIS_URL:
    CACHES = {  # type: ignore
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        }
    }

    # Сессии в Redis
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"

# Sentry мониторинг ошибок
SENTRY_DSN = os.environ.get("SENTRY_DSN")
if SENTRY_DSN and sentry_sdk:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True,
        environment="production",
    )

# Логирование в файл
LOGGING["handlers"]["file"]["level"] = "ERROR"  # type: ignore
LOGGING["loggers"]["django"]["handlers"] = ["console", "file"]  # type: ignore

# Выводим информацию (без секретов)
print("=" * 50)
print("🚀 ПРОДАКШЕН: PRODUCTION MODE")
print(f"🌐 Allowed hosts: {len(ALLOWED_HOSTS)} хостов")
print(f"📁 Database: {DATABASES['default']['ENGINE']}")
print(f"🤖 Telegram Bot: {'✅ Настроен' if TELEGRAM_BOT_TOKEN else '❌ Не настроен'}")
print(f"📧 Email: {EMAIL_HOST}:{EMAIL_PORT}")
print("=" * 50)

# Проверка обязательных переменных
required_vars = ["SECRET_KEY", "DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST"]
missing_vars = [var for var in required_vars if not os.environ.get(var)]
if missing_vars:
    raise ValueError(
        f"Missing required environment variables: {', '.join(missing_vars)}"
    )
