import pytest
from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()


@pytest.fixture
def api_client():
    """Фикстура для API клиента"""
    return Client()


@pytest.fixture
def admin_user():
    """Фикстура для пользователя-администратора"""
    return User.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="admin123",
        role="admin",
        is_staff=True,
    )


@pytest.fixture
def manager_user():
    """Фикстура для пользователя-менеджера"""
    return User.objects.create_user(
        username="manager",
        email="manager@example.com",
        password="manager123",
        role="manager",
    )


@pytest.fixture
def employee_user():
    """Фикстура для пользователя-сотрудника"""
    return User.objects.create_user(
        username="employee",
        email="employee@example.com",
        password="employee123",
        role="employee",
    )


@pytest.fixture
def test_file():
    """Фикстура для тестового файла"""
    from django.core.files.uploadedfile import SimpleUploadedFile

    return SimpleUploadedFile(
        name="test.jpg", content=b"test content", content_type="image/jpeg"
    )
