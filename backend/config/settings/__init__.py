"""
Выбор конфигурации в зависимости от окружения
"""

import os

ENVIRONMENT = os.getenv("DJANGO_ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    from .production import *  # noqa: F403, F401
elif ENVIRONMENT == "testing":
    from .testing import *  # noqa: F403, F401
elif ENVIRONMENT == "docker":
    from .docker import *  # noqa: F403, F401
else:
    from .development import *  # noqa: F403, F401

# Подавляем предупреждения Flake8 для звездочных импортов
# Это необходимо для правильной работы Django
__all__ = []  # Пустой __all__ чтобы успокоить linter
