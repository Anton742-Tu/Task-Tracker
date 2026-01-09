from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from api.permissions.permissions import IsAdminUser, IsManagerOrAdmin
from apps.projects.models import Project

User = get_user_model()


class PermissionsTest(TestCase):
    """Тесты для permission классов."""

    def setUp(self):
        self.factory = APIRequestFactory()
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
        self.project = Project.objects.create(name="Test Project", creator=self.manager)
        self.project.members.add(self.employee, self.manager, self.admin)

    def test_is_admin_user_permission(self):
        """Тест IsAdminUser permission."""
        permission = IsAdminUser()

        # Правильный способ: создаем request и устанавливаем user
        anon_request = self.factory.get("/")
        anon_request.user = AnonymousUser()

        employee_request = self.factory.get("/")
        employee_request.user = self.employee

        manager_request = self.factory.get("/")
        manager_request.user = self.manager

        admin_request = self.factory.get("/")
        admin_request.user = self.admin

        # Аноним не должен иметь доступ
        self.assertFalse(permission.has_permission(anon_request, None))

        # Сотрудник не админ
        self.assertFalse(permission.has_permission(employee_request, None))

        # Менеджер не админ
        self.assertFalse(permission.has_permission(manager_request, None))

        # Админ должен иметь доступ
        self.assertTrue(permission.has_permission(admin_request, None))

        print("✓ IsAdminUser: только админы имеют доступ")

    def test_is_manager_or_admin_permission(self):
        """Тест IsManagerOrAdmin permission."""
        permission = IsManagerOrAdmin()

        # Создаем requests с пользователями
        anon_request = self.factory.get("/")
        anon_request.user = AnonymousUser()

        employee_request = self.factory.get("/")
        employee_request.user = self.employee

        manager_request = self.factory.get("/")
        manager_request.user = self.manager

        admin_request = self.factory.get("/")
        admin_request.user = self.admin

        # Аноним не должен иметь доступ
        self.assertFalse(permission.has_permission(anon_request, None))

        # Сотрудник не менеджер/админ
        self.assertFalse(permission.has_permission(employee_request, None))

        # Менеджер должен иметь доступ
        self.assertTrue(permission.has_permission(manager_request, None))

        # Админ должен иметь доступ
        self.assertTrue(permission.has_permission(admin_request, None))

        print("✓ IsManagerOrAdmin: менеджеры и админы имеют доступ")

    def test_is_project_member_or_admin_permission(self):
        """Тест IsProjectMemberOrAdmin permission."""
        from api.permissions.permissions import IsProjectMemberOrAdmin

        permission = IsProjectMemberOrAdmin()

        # Запрос от сотрудника (участник проекта)
        employee_request = self.factory.get("/")
        employee_request.user = self.employee

        # Запрос от менеджера (создатель проекта)
        manager_request = self.factory.get("/")
        manager_request.user = self.manager

        # Запрос от админа
        admin_request = self.factory.get("/")
        admin_request.user = self.admin

        # Сотрудник - участник проекта
        self.assertTrue(
            permission.has_object_permission(employee_request, None, self.project)
        )

        # Менеджер - создатель проекта
        self.assertTrue(
            permission.has_object_permission(manager_request, None, self.project)
        )

        # Админ
        self.assertTrue(
            permission.has_object_permission(admin_request, None, self.project)
        )

        print("✓ IsProjectMemberOrAdmin: участники проекта и админы имеют доступ")

    def test_is_task_assignee_or_admin_permission(self):
        """Тест IsTaskAssigneeOrAdmin permission."""
        from api.permissions.permissions import IsTaskAssigneeOrAdmin
        from apps.tasks.models import Task

        # Создаем задачу
        task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            project=self.project,
            creator=self.manager,
            assignee=self.employee,
            status="todo",
        )

        permission = IsTaskAssigneeOrAdmin()

        # Запрос от сотрудника (исполнитель задачи)
        employee_request = self.factory.get("/")
        employee_request.user = self.employee

        # Запрос от менеджера (не исполнитель)
        manager_request = self.factory.get("/")
        manager_request.user = self.manager

        # Запрос от админа
        admin_request = self.factory.get("/")
        admin_request.user = self.admin

        # Сотрудник - исполнитель задачи
        self.assertTrue(permission.has_object_permission(employee_request, None, task))

        # Менеджер - не исполнитель
        self.assertFalse(permission.has_object_permission(manager_request, None, task))

        # Админ
        self.assertTrue(permission.has_object_permission(admin_request, None, task))

        print("✓ IsTaskAssigneeOrAdmin: исполнитель задачи и админы имеют доступ")

    def test_user_permissions_model(self):
        """Тест свойств is_admin, is_manager модели User."""
        # Проверяем свойства
        self.assertFalse(self.employee.is_admin)
        self.assertFalse(self.employee.is_manager)

        self.assertFalse(self.manager.is_admin)
        self.assertTrue(self.manager.is_manager)

        self.assertTrue(self.admin.is_admin)
        self.assertTrue(self.admin.is_manager)

        print("✓ Свойства is_admin/is_manager работают корректно")
