import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    """Фикстура для API клиента."""
    return APIClient()


@pytest.fixture
def authenticated_api_client():
    """Фикстура для аутентифицированного API клиента."""
    client = APIClient()
    user = User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def admin_api_client():
    """Фикстура для API клиента администратора."""
    client = APIClient()
    admin_user = User.objects.create_superuser(
        username="admin", email="admin@example.com", password="adminpass123"
    )
    client.force_authenticate(user=admin_user)
    return client


@pytest.fixture
def sample_user():
    """Фикстура для тестового пользователя."""
    return User.objects.create_user(
        username="sampleuser",
        email="sample@example.com",
        password="samplepass123",
        role="employee",
    )


@pytest.fixture
def sample_manager():
    """Фикстура для тестового менеджера."""
    return User.objects.create_user(
        username="manager",
        email="manager@example.com",
        password="managerpass123",
        role="manager",
    )
