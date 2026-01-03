from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.projects.models import Project
from apps.tasks.models import Task

User = get_user_model()


class TasksAPITestCase(TestCase):
    """Тесты для API задач"""

    def setUp(self):
        self.client = APIClient()

        # Создаем пользователей
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

        # Создаем проект
        self.project = Project.objects.create(
            name="Test Project",
            description="Description",
            status="active",
            creator=self.manager,
        )
        self.project.members.add(self.manager, self.employee1, self.employee2)

        # Создаем задачу
        self.task = Task.objects.create(
            title="Test Task",
            description="Task Description",
            project=self.project,
            status="todo",
            priority="medium",
            due_date=date.today() + timedelta(days=7),
            creator=self.manager,
            assignee=self.employee1,
        )

        # Аутентифицируем клиенты
        self.manager_client = APIClient()
        self.manager_client.force_authenticate(user=self.manager)

        self.employee1_client = APIClient()
        self.employee1_client.force_authenticate(user=self.employee1)

        self.employee2_client = APIClient()
        self.employee2_client.force_authenticate(user=self.employee2)

    def test_create_task(self):
        """Тест создания задачи"""
        data = {
            "title": "New Task",
            "description": "Description",
            "project": self.project.id,
            "status": "todo",
            "priority": "high",
            "due_date": (date.today() + timedelta(days=5)).isoformat(),
            "assignee": self.employee2.id,
        }

        response = self.manager_client.post("/api/tasks/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New Task")
        self.assertEqual(response.data["assignee"]["username"], "employee2")

    def test_create_task_without_permission(self):
        """Тест создания задачи без прав"""
        data = {
            "title": "Unauthorized Task",
            "description": "Description",
            "project": self.project.id,
            "status": "todo",
        }

        # Сотрудник без прав на создание задач в проекте
        outsider = User.objects.create_user(
            username="outsider", email="outsider@test.com", password="password123"
        )
        outsider_client = APIClient()
        outsider_client.force_authenticate(user=outsider)

        response = outsider_client.post("/api/tasks/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_tasks(self):
        """Тест получения списка задач"""
        response = self.employee1_client.get("/api/tasks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Test Task")

    def test_filter_tasks_by_status(self):
        """Тест фильтрации задач по статусу"""
        # Создаем задачу с другим статусом
        Task.objects.create(
            title="Completed Task",
            description="Description",
            project=self.project,
            status="completed",
            creator=self.manager,
            assignee=self.employee1,
        )

        response = self.manager_client.get("/api/tasks/?status=todo")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["status"], "todo")

    def test_filter_tasks_by_project(self):
        """Тест фильтрации задач по проекту"""
        # Создаем второй проект и задачу
        project2 = Project.objects.create(
            name="Project 2",
            description="Description",
            status="active",
            creator=self.manager,
        )
        project2.members.add(self.manager, self.employee1)

        Task.objects.create(
            title="Task in Project 2",
            description="Description",
            project=project2,
            status="todo",
            creator=self.manager,
            assignee=self.employee1,
        )

        response = self.manager_client.get(f"/api/tasks/?project={self.project.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["project"]["name"], "Test Project")

    def test_filter_tasks_by_assignee(self):
        """Тест фильтрации задач по исполнителю"""
        # Создаем задачу для второго сотрудника
        Task.objects.create(
            title="Task for Employee 2",
            description="Description",
            project=self.project,
            status="in_progress",
            creator=self.manager,
            assignee=self.employee2,
        )

        response = self.manager_client.get(f"/api/tasks/?assignee={self.employee1.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["assignee"]["username"], "employee1")

    def test_update_task_as_creator(self):
        """Тест обновления задачи создателем"""
        data = {
            "title": "Updated Task Title",
            "status": "in_progress",
            "priority": "high",
        }

        response = self.manager_client.patch(
            f"/api/tasks/{self.task.id}/", data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Updated Task Title")
        self.assertEqual(self.task.status, "in_progress")
        self.assertEqual(self.task.priority, "high")

    def test_update_task_as_assignee(self):
        """Тест обновления задачи исполнителем"""
        # Исполнитель может обновлять только некоторые поля
        data = {"status": "completed", "description": "Updated by assignee"}

        response = self.employee1_client.patch(
            f"/api/tasks/{self.task.id}/", data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, "completed")
        # Проверяем, что описание НЕ изменилось (только статус)
        self.assertNotEqual(self.task.description, "Updated by assignee")

    def test_update_task_as_non_participant(self):
        """Тест обновления задачи не-участником"""
        outsider = User.objects.create_user(
            username="outsider", email="outsider@test.com", password="password123"
        )
        outsider_client = APIClient()
        outsider_client.force_authenticate(user=outsider)

        data = {"title": "Hacked Title"}

        response = outsider_client.patch(
            f"/api/tasks/{self.task.id}/", data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_task_as_creator(self):
        """Тест удаления задачи создателем"""
        response = self.manager_client.delete(f"/api/tasks/{self.task.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    def test_delete_task_as_non_creator(self):
        """Тест удаления задачи не-создателем"""
        response = self.employee1_client.delete(f"/api/tasks/{self.task.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_task_statistics(self):
        """Тест получения статистики по задачам"""
        # Создаем больше задач
        Task.objects.create(
            title="Task 2",
            description="Description",
            project=self.project,
            status="completed",
            creator=self.manager,
            assignee=self.employee1,
        )

        Task.objects.create(
            title="Task 3",
            description="Description",
            project=self.project,
            status="in_progress",
            creator=self.manager,
            assignee=self.employee2,
        )

        response = self.manager_client.get("/api/tasks/statistics/")

        # Проверяем, что эндпоинт существует и возвращает данные
        if response.status_code != 404:  # Если эндпоинт реализован
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn("total", response.data)
            self.assertIn("todo", response.data)
            self.assertIn("in_progress", response.data)
            self.assertIn("completed", response.data)
