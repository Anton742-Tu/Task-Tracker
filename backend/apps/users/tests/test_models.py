import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


User = get_user_model()


class TestUserModel:
    """Тесты для модели User."""

    def test_create_user(self):
        """Тест создания обычного пользователя."""
        user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.check_password("testpass123")
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.role == "employee"

    def test_create_superuser(self):
        """Тест создания суперпользователя."""
        admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )

        assert admin_user.is_superuser is True
        assert admin_user.is_staff is True
        assert admin_user.role == "admin"

    def test_user_string_representation(self):
        """Тест строкового представления пользователя."""
        user = User.objects.create_user(
            username="johndoe",
            email="john@example.com",
            first_name="John",
            last_name="Doe",
        )

        assert str(user) == "John Doe (employee)"

    def test_user_without_name(self):
        """Тест пользователя без имени."""
        user = User.objects.create_user(username="username", email="user@example.com")

        assert str(user) == "username (employee)"

    def test_user_role_properties(self):
        """Тест свойств ролей пользователя."""
        # Employee
        employee = User.objects.create_user(username="employee", role="employee")
        assert employee.is_manager is False
        assert employee.is_admin is False

        # Manager
        manager = User.objects.create_user(username="manager", role="manager")
        assert manager.is_manager is True
        assert manager.is_admin is False

        # Admin
        admin = User.objects.create_user(username="admin", role="admin")
        assert admin.is_manager is True
        assert admin.is_admin is True

    @pytest.mark.parametrize("role", ["employee", "manager", "admin"])
    def test_valid_roles(self, role):
        """Тест валидных ролей пользователя."""
        user = User.objects.create_user(username=f"test_{role}", role=role)
        assert user.role == role

    def test_invalid_role(self):
        """Тест невалидной роли пользователя."""
        with pytest.raises(ValidationError):
            user = User(username="invalid", role="invalid_role")
            user.full_clean()
