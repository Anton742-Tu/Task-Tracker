import os

import pytest

# Устанавливаем переменную окружения для тестов
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


def pytest_configure():
    """Настройка pytest для Django"""
    import django

    django.setup()

    # Отключаем Debug Toolbar если он есть
    from django.conf import settings

    if "debug_toolbar" in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS.remove("debug_toolbar")

    if "debug_toolbar.middleware.DebugToolbarMiddleware" in settings.MIDDLEWARE:
        settings.MIDDLEWARE.remove("debug_toolbar.middleware.DebugToolbarMiddleware")


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Даем доступ к БД всем тестам"""
    pass


@pytest.fixture
def api_client():
    """Фикстура для API клиента"""
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def authenticated_client(api_client, django_user_model):
    """Фикстура для аутентифицированного клиента"""
    user = django_user_model.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )

    # Получаем токен
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    return api_client, user
