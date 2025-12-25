import pytest
from django.contrib.auth import get_user_model

from apps.projects.models import Project


User = get_user_model()


class TestProjectModel:
    """Тесты для модели Project."""

    def test_create_project(self, sample_user):
        """Тест создания проекта."""
        project = Project.objects.create(name="Test Project", description="Test description", creator=sample_user)

        assert project.name == "Test Project"
        assert project.description == "Test description"
        assert project.creator == sample_user
        assert str(project) == "Test Project"

    def test_project_string_representation(self, sample_user):
        """Тест строкового представления проекта."""
        project = Project.objects.create(name="My Project", creator=sample_user)

        assert str(project) == "My Project"

    def test_project_created_at_auto_now_add(self, sample_user):
        """Тест автоматического добавления created_at."""
        project = Project.objects.create(name="Test Project", creator=sample_user)

        assert project.created_at is not None
