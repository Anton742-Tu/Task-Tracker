from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.projects.models import Project

User = get_user_model()


class ProjectsAPITestCase(TestCase):
    """Тесты для API проектов"""

    def setUp(self):
        self.client = APIClient()

        # Создаем пользователей
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="password123",
            role="admin",
        )

        self.manager = User.objects.create_user(
            username="manager",
            email="manager@test.com",
            password="password123",
            role="manager",
        )

        self.employee = User.objects.create_user(
            username="employee",
            email="employee@test.com",
            password="password123",
            role="employee",
        )

        # Создаем проект
        self.project = Project.objects.create(
            name="Test Project",
            description="Test Description",
            status="active",
            creator=self.manager,
        )
        self.project.members.add(self.manager, self.employee)

        # Аутентифицируем клиенты
        self.admin_client = APIClient()
        self.admin_client.force_authenticate(user=self.admin)

        self.manager_client = APIClient()
        self.manager_client.force_authenticate(user=self.manager)

        self.employee_client = APIClient()
        self.employee_client.force_authenticate(user=self.employee)

        self.anonymous_client = APIClient()

    def test_create_project_as_manager(self):
        """Тест создания проекта менеджером"""
        data = {
            "name": "New Project",
            "description": "New Description",
            "status": "active",
            "members": [self.employee.id],
        }

        response = self.manager_client.post("/api/projects/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Project")
        self.assertEqual(response.data["creator"]["username"], "manager")

    def test_create_project_as_employee(self):
        """Тест создания проекта сотрудником (должен быть запрещен)"""
        data = {
            "name": "Employee Project",
            "description": "Description",
            "status": "active",
        }

        response = self.employee_client.post("/api/projects/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_projects(self):
        """Тест получения списка проектов"""
        response = self.employee_client.get("/api/projects/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_project(self):
        """Тест получения конкретного проекта"""
        response = self.employee_client.get(f"/api/projects/{self.project.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Project")

    def test_update_project_as_creator(self):
        """Тест обновления проекта создателем"""
        data = {"name": "Updated Project", "description": "Updated Description"}

        response = self.manager_client.patch(
            f"/api/projects/{self.project.id}/", data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, "Updated Project")

    def test_update_project_as_non_creator(self):
        """Тест обновления проекта не-создателем"""
        data = {"name": "Unauthorized Update"}

        response = self.employee_client.patch(
            f"/api/projects/{self.project.id}/", data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project_as_admin(self):
        """Тест удаления проекта администратором"""
        response = self.admin_client.delete(f"/api/projects/{self.project.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())

    def test_filter_projects_by_status(self):
        """Тест фильтрации проектов по статусу"""
        # Создаем архивный проект
        Project.objects.create(
            name="Archived Project",
            description="Description",
            status="archived",
            creator=self.manager,
        )

        response = self.manager_client.get("/api/projects/?status=active")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["status"], "active")

    def test_search_projects(self):
        """Тест поиска проектов"""
        response = self.manager_client.get("/api/projects/?search=Test")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        response = self.manager_client.get("/api/projects/?search=Nonexistent")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
