"""
Настройки для Docker окружения
"""

import os
from .development import *  # type: ignore

# Override database for Docker
DATABASES["default"]["HOST"] = os.getenv("DB_HOST", "postgres")  # type: ignore
DATABASES["default"]["PORT"] = os.getenv("DB_PORT", "5432")  # type: ignore

# Update allowed hosts
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "backend"]


# Debug toolbar для Docker
def show_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
}

print("=" * 50)
print("🐳 DOCKER: CONTAINER MODE")
print(f"📁 Database host: {DATABASES['default']['HOST']}")
print("=" * 50)
