import pytest
import logging
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.files.models import FileAttachment
from apps.projects.models import Project
from apps.tasks.models import Task

User = get_user_model()


def pytest_configure():
    """Настройка pytest"""
    # Отключаем логирование WARNING для тестов
    logging.getLogger().setLevel(logging.ERROR)

    # Или отключаем логирование конкретных логгеров Django
    logging.getLogger("django.request").setLevel(logging.ERROR)
    logging.getLogger("django.security").setLevel(logging.ERROR)


@pytest.fixture(autouse=True)
def disable_logging():
    """Отключает логирование для всех тестов"""
    import logging

    logging.disable(logging.WARNING)
    yield
    logging.disable(logging.NOTSET)


@pytest.fixture
def test_user():
    """Создание тестового пользователя"""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        role="employee",
    )


@pytest.fixture
def test_manager():
    """Создание тестового менеджера"""
    return User.objects.create_user(
        username="testmanager",
        email="manager@example.com",
        password="testpass123",
        role="manager",
    )


@pytest.fixture
def test_project(test_manager, test_user):
    """Создание тестового проекта"""
    project = Project.objects.create(
        name="Test Project",
        description="Test Description",
        status="active",
        creator=test_manager,
    )
    project.members.add(test_manager, test_user)
    return project


@pytest.fixture
def test_task(test_project, test_manager, test_user):
    """Создание тестовой задачи"""
    return Task.objects.create(
        title="Test Task",
        description="Task Description",
        project=test_project,
        status="todo",
        priority="medium",
        assignee=test_user,
        # Если есть поле created_by:
        created_by=test_manager,  # или creator
    )


@pytest.fixture
def test_file(test_project, test_manager):
    """Создание тестового файла"""
    test_file = SimpleUploadedFile(
        name="test.jpg", content=b"test content", content_type="image/jpeg"
    )

    return FileAttachment.objects.create(
        file=test_file,
        original_filename="test.jpg",
        file_type="image",
        mime_type="image/jpeg",
        file_size=1000,
        project=test_project,
        uploaded_by=test_manager,
        description="Test file",
    )
