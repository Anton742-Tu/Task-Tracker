import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class ProjectWorkflowTestCase(TestCase):
    """Интеграционные тесты полного workflow проекта"""

    def setUp(self):
        self.client = APIClient()

        # Создаем менеджера и сотрудников с уникальными именами
        timestamp = uuid.uuid4().hex[:8]

        self.manager = User.objects.create_user(
            username=f"manager_{timestamp}",
            email=f"manager_{timestamp}@test.com",
            password="password123",
            role="manager",
        )

        self.employee1 = User.objects.create_user(
            username=f"employee1_{timestamp}",
            email=f"employee1_{timestamp}@test.com",
            password="password123",
            role="employee",
        )

        self.employee2 = User.objects.create_user(
            username=f"employee2_{timestamp}",
            email=f"employee2_{timestamp}@test.com",
            password="password123",
            role="employee",
        )

        # Аутентифицируем менеджера
        self.manager_client = APIClient()
        self.manager_client.force_authenticate(user=self.manager)

        self.employee1_client = APIClient()
        self.employee1_client.force_authenticate(user=self.employee1)

    def test_complete_project_workflow(self):
        """Упрощенный workflow проекта: только создание проекта и задач"""
        print("\n=== Starting simplified project workflow test ===")

        # 1. Создаем проект - ИСПОЛЬЗУЕМ REVERSE
        try:
            # Пробуем получить URL по имени
            project_list_url = reverse("project-list")  # Для ViewSet это 'project-list'
        except Exception:
            # Если не находит по имени, используем прямой URL
            project_list_url = "/api/projects/"

        project_data = {
            "name": "Simple Test Project",
            "description": "Простой тестовый проект",
            "status": "active",
            "members": [self.employee1.id, self.employee2.id],
        }

        response = self.manager_client.post(
            project_list_url, project_data, format="json"
        )
        print(f"1. Create project at {project_list_url}: {response.status_code}")

        # Проверяем если это редирект (301)
        if response.status_code == 301:
            print(f"   Redirect detected to: {response.url}")
            # Следуем за редиректом с follow=True
            response = self.manager_client.post(
                project_list_url, project_data, format="json", follow=True
            )
            print(f"   After follow: {response.status_code}")

        # Отладочная информация
        print(f"   Response headers: {dict(response.headers)}")
        if hasattr(response, "data"):
            print(f"   Response data: {response.data}")
        else:
            print(f"   Response content: {response.content}")

        # Ожидаем 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Получаем ID проекта
        if response.status_code == 201:
            project_id = response.data.get("id")
        else:
            # Если не 201, пытаемся найти проект другим способом
            from apps.projects.models import Project

            project = Project.objects.filter(name="Simple Test Project").first()
            project_id = project.id if project else None
            if not project_id:
                self.skipTest("Could not create or find project")
                return

        print(f"   Project ID: {project_id}")

        # 2. Создаем задачу - ИСПОЛЬЗУЕМ REVERSE
        try:
            task_list_url = reverse("task-list")  # Для ViewSet это 'task-list'
        except Exception:
            task_list_url = "/api/tasks/"

        task_data = {
            "title": "Test Task",
            "description": "Test description",
            "project": project_id,
            "status": "todo",
            "priority": "medium",
            "assignee": self.employee1.id,  # Добавляем assignee
        }

        response = self.manager_client.post(task_list_url, task_data, format="json")
        print(f"2. Create task at {task_list_url}: {response.status_code}")

        # Проверяем редирект
        if response.status_code == 301:
            print(f"   Redirect detected to: {response.url}")
            response = self.manager_client.post(
                task_list_url, task_data, format="json", follow=True
            )
            print(f"   After follow: {response.status_code}")

        # Проверяем результат
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        print("✅ Basic project workflow test passed!")
