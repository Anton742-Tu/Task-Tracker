from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from apps.users.permissions import IsAdminUser, IsEmployeeOrHigher, IsManagerOrAdmin

User = get_user_model()


class UserPermissionsTest(TestCase):
    """Тесты для permissions из apps.users."""

    def setUp(self):
        self.employee = User.objects.create_user(
            username="employee",
            email="employee@example.com",
            password="password123",
            role="employee",
        )
        self.manager = User.objects.create_user(
            username="manager",
            email="manager@example.com",
            password="manager123",
            role="manager",
        )
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="admin123",
            role="admin",
        )

    def test_is_admin_user_permission(self):
        """Тест IsAdminUser permission."""
        permission = IsAdminUser()

        class MockRequest:
            def __init__(self, user):
                self.user = user

        # Аноним
        anon_request = MockRequest(AnonymousUser())
        self.assertFalse(permission.has_permission(anon_request, None))

        # Сотрудник
        employee_request = MockRequest(self.employee)
        self.assertFalse(permission.has_permission(employee_request, None))

        # Менеджер
        manager_request = MockRequest(self.manager)
        self.assertFalse(permission.has_permission(manager_request, None))

        # Админ
        admin_request = MockRequest(self.admin)
        self.assertTrue(permission.has_permission(admin_request, None))

        print("✓ IsAdminUser: только админы имеют доступ")

    def test_is_manager_or_admin_permission(self):
        """Тест IsManagerOrAdmin permission."""
        permission = IsManagerOrAdmin()

        class MockRequest:
            def __init__(self, user):
                self.user = user

        # Аноним
        anon_request = MockRequest(AnonymousUser())
        self.assertFalse(permission.has_permission(anon_request, None))

        # Сотрудник
        employee_request = MockRequest(self.employee)
        self.assertFalse(permission.has_permission(employee_request, None))

        # Менеджер
        manager_request = MockRequest(self.manager)
        self.assertTrue(permission.has_permission(manager_request, None))

        # Админ
        admin_request = MockRequest(self.admin)
        self.assertTrue(permission.has_permission(admin_request, None))

        print("✓ IsManagerOrAdmin: менеджеры и админы имеют доступ")

    def test_is_employee_or_higher_permission(self):
        """Тест IsEmployeeOrHigher permission."""
        permission = IsEmployeeOrHigher()

        class MockRequest:
            def __init__(self, user):
                self.user = user

        # Аноним
        anon_request = MockRequest(AnonymousUser())
        self.assertFalse(permission.has_permission(anon_request, None))

        # Сотрудник (и выше) должны иметь доступ
        employee_request = MockRequest(self.employee)
        self.assertTrue(permission.has_permission(employee_request, None))

        manager_request = MockRequest(self.manager)
        self.assertTrue(permission.has_permission(manager_request, None))

        admin_request = MockRequest(self.admin)
        self.assertTrue(permission.has_permission(admin_request, None))

        print("✓ IsEmployeeOrHigher: все аутентифицированные имеют доступ")

    def test_permission_classes_can_be_imported(self):
        """Тест что все permission классы можно импортировать."""
        from apps.users.permissions import (
            IsAdminUser,
            IsEmployeeOrHigher,
            IsManagerOrAdmin,
            IsProjectMember,
        )

        # Создаем экземпляры
        admin_perm = IsAdminUser()
        manager_perm = IsManagerOrAdmin()
        employee_perm = IsEmployeeOrHigher()
        project_perm = IsProjectMember()

        self.assertIsNotNone(admin_perm)
        self.assertIsNotNone(manager_perm)
        self.assertIsNotNone(employee_perm)
        self.assertIsNotNone(project_perm)

        print("✓ Все permission классы успешно импортированы")
