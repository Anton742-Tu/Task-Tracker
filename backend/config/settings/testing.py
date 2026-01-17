"""
Настройки для тестирования
"""

import os
from datetime import timedelta
from .base import *  # type: ignore

# Debug mode
DEBUG = False

# Секретный ключ для тестов
SECRET_KEY = "test-secret-key-for-tests-only-12345"

# Разрешенные хосты
ALLOWED_HOSTS = ["testserver", "localhost"]

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Ускоряем тесты
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Отключаем кэширование для тестов
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Отключаем WhiteNoise для тестов
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
# Создаем новый список middleware без whitenoise
middleware_without_whitenoise = []
for m in MIDDLEWARE:  # type: ignore
    if m != "whitenoise.middleware.WhiteNoiseMiddleware":
        middleware_without_whitenoise.append(m)
MIDDLEWARE = middleware_without_whitenoise  # type: ignore

# Отключаем CORS для тестов
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = []

# Тестовые настройки email
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Уменьшаем время жизни токенов для тестов
SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] = timedelta(minutes=5)  # type: ignore
SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"] = timedelta(hours=1)  # type: ignore

# Тестовые медиа файлы
MEDIA_ROOT = BASE_DIR / "test_media"  # type: ignore
os.makedirs(MEDIA_ROOT, exist_ok=True)

# Настройки для тестов
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# Выводим информацию
print("=" * 50)
print("🧪 ТЕСТИРОВАНИЕ: TEST MODE")
print(f"📁 Database: {DATABASES['default']['ENGINE']}")
print("=" * 50)
