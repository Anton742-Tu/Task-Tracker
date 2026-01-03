from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class ProjectWorkflowTestCase(TestCase):
    """Интеграционные тесты полного workflow проекта"""

    def setUp(self):
        self.client = APIClient()

        # Создаем менеджера и сотрудников
        self.manager = User.objects.create_user(
            username="manager",
            email="manager@test.com",
            password="password123",
            role="manager",
        )

        self.employee1 = User.objects.create_user(
            username="employee1",
            email="employee1@test.com",
            password="password123",
            role="employee",
        )

        self.employee2 = User.objects.create_user(
            username="employee2",
            email="employee2@test.com",
            password="password123",
            role="employee",
        )

        # Аутентифицируем менеджера
        self.manager_client = APIClient()
        self.manager_client.force_authenticate(user=self.manager)

        self.employee1_client = APIClient()
        self.employee1_client.force_authenticate(user=self.employee1)

    def test_complete_project_workflow(self):
        """Полный workflow проекта: создание → задачи → файлы"""
        # 1. Создаем проект
        project_data = {
            "name": "New Software Project",
            "description": "Разработка нового ПО",
            "status": "active",
            "members": [self.employee1.id, self.employee2.id],
        }

        response = self.manager_client.post(
            "/api/projects/", project_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        project_id = response.data["id"]

        # 2. Создаем задачи в проекте
        tasks_data = [
            {
                "title": "Дизайн интерфейса",
                "description": "Создать макеты интерфейса",
                "project": project_id,
                "status": "todo",
                "priority": "high",
                "assignee": self.employee1.id,
            },
            {
                "title": "Настройка БД",
                "description": "Настроить базу данных",
                "project": project_id,
                "status": "in_progress",
                "priority": "medium",
                "assignee": self.employee2.id,
            },
        ]

        for task_data in tasks_data:
            response = self.manager_client.post("/api/tasks/", task_data, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 3. Получаем список задач проекта
        response = self.manager_client.get(f"/api/tasks/?project={project_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # 4. Загружаем файл в задачу
        task_id = response.data[0]["id"]
        test_file = SimpleUploadedFile(
            name="design.jpg", content=b"design content", content_type="image/jpeg"
        )

        file_data = {
            "file": test_file,
            "task_id": task_id,
            "description": "Макет интерфейса",
            "is_public": True,
        }

        response = self.employee1_client.post(
            "/api/files/upload/", file_data, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # file_id = response.data["file"]["id"]  # Временно закоментированно!

        # 5. Обновляем статус задачи
        update_data = {"status": "completed"}
        response = self.employee1_client.patch(
            f"/api/tasks/{task_id}/", update_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 6. Получаем статистику по проекту
        response = self.manager_client.get(f"/api/projects/{project_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "New Software Project")

        # 7. Архивируем проект
        archive_data = {"status": "archived"}
        response = self.manager_client.patch(
            f"/api/projects/{project_id}/", archive_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что проект архивирован
        response = self.manager_client.get(f"/api/projects/{project_id}/")
        self.assertEqual(response.data["status"], "archived")
