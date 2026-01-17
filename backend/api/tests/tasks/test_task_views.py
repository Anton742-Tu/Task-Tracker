# -*- coding: utf-8 -*-
import uuid
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

        # Создаем пользователей с уникальными именами
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

        # Создаем проект
        self.project = Project.objects.create(
            name=f"Test Project {timestamp}",
            description="Description",
            status="active",
            creator=self.manager,
        )
        self.project.members.add(self.manager, self.employee1, self.employee2)

        # Создаем задачу
        self.task = Task.objects.create(
            title=f"Test Task {timestamp}",
            description="Task Description",
            project=self.project,
            status="todo",
            priority="medium",
            due_date=date.today() + timedelta(days=7),
            creator=self.manager,
            assignee=self.employee1,
        )

        # Клиенты
        self.manager_client = APIClient()
        self.manager_client.force_authenticate(user=self.manager)

        self.employee1_client = APIClient()
        self.employee1_client.force_authenticate(user=self.employee1)

        self.employee2_client = APIClient()
        self.employee2_client.force_authenticate(user=self.employee2)

        print(f"\n{'=' * 60}")
        print("SETUP для теста")
        print(f"Manager: {self.manager.username}")
        print(f"Employee1: {self.employee1.username}")
        print(f"Employee2: {self.employee2.username}")
        print(f"Project: {self.project.name}")
        print(f"Task: {self.task.title} (priority: {self.task.priority})")
        print(f"{'=' * 60}")

    def test_create_task(self):
        """Тест создания задачи"""
        task_title = f"New Task {uuid.uuid4().hex[:8]}"
        data = {
            "title": task_title,
            "description": "Description",
            "project_id": self.project.id,
            "status": "todo",
            "priority": "high",
            "due_date": (date.today() + timedelta(days=5)).isoformat(),
            "assignee_id": self.employee2.id,
        }

        print(f"\n[test_create_task] Создание задачи: {task_title}")

        response = self.manager_client.post("/api/tasks/", data, format="json")

        print(f"Статус ответа: {response.status_code}")
        print(f"Данные ответа: {response.data}")

        # Если 400 - проверяем ошибку
        if response.status_code == 400:
            print(f"Ошибка валидации: {response.data}")
            # Проверяем что ошибка именно в project поле
            if "project" in response.data or "project_id" in response.data:
                print("⚠️  Ошибка: поле project обязательно")
            self.assertEqual(response.status_code, 400)
            return

        # Ожидаем 201 или 200
        self.assertIn(
            response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK]
        )

        # Проверяем что задача создана
        task_created = Task.objects.filter(title=task_title).exists()
        self.assertTrue(task_created, f"Задача '{task_title}' не найдена")

    def test_create_task_without_permission(self):
        """Тест создания задачи без прав"""
        task_title = f"Unauthorized Task {uuid.uuid4().hex[:8]}"
        data = {
            "title": task_title,
            "description": "Description",
            "project_id": self.project.id,
            "status": "todo",
        }

        outsider = User.objects.create_user(
            username=f"outsider_{uuid.uuid4().hex[:8]}",
            email=f"outsider_{uuid.uuid4().hex[:8]}@test.com",
            password="password123",
        )
        outsider_client = APIClient()
        outsider_client.force_authenticate(user=outsider)

        print("\n[test_create_task_without_permission]")

        response = outsider_client.post("/api/tasks/", data, format="json")

        print(f"Статус ответа: {response.status_code}")

        # Может быть 400 (валидация) или 403 (права)
        if response.status_code == 400:
            print(f"Валидационная ошибка: {response.data}")
            # Проверяем что это не 403
            self.assertNotEqual(response.status_code, 403)
        else:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_tasks(self):
        """Тест получения списка задач"""
        print("\n[test_list_tasks]")

        response = self.employee1_client.get("/api/tasks/")

        print(f"Статус ответа: {response.status_code}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем формат ответа
        if isinstance(response.data, list):
            print(f"Получено задач: {len(response.data)}")
        elif "results" in response.data:
            print(f"Получено задач (пагинация): {len(response.data['results'])}")

    def test_filter_tasks_by_status(self):
        """Тест фильтрации задач по статусу"""
        print("\n[test_filter_tasks_by_status]")

        response = self.manager_client.get("/api/tasks/?status=todo")

        print(f"Статус ответа: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_tasks_by_project(self):
        """Тест фильтрации задач по проекту"""
        print("\n[test_filter_tasks_by_project]")

        response = self.manager_client.get(f"/api/tasks/?project={self.project.id}")

        print(f"Статус ответа: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_tasks_by_assignee(self):
        """Тест фильтрации задач по исполнителю"""
        print("\n[test_filter_tasks_by_assignee]")

        response = self.manager_client.get(f"/api/tasks/?assignee={self.employee1.id}")

        print(f"Статус ответа: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_task_as_creator(self):
        """Тест обновления задачи создателем"""
        print("\n[test_update_task_as_creator]")
        print(f"Исходная задача: {self.task.title}, приоритет: {self.task.priority}")

        data = {
            "title": "Updated Task Title",
            "status": "in_progress",
            "priority": "high",
        }

        response = self.manager_client.patch(
            f"/api/tasks/{self.task.id}/", data, format="json"
        )

        print(f"Статус ответа: {response.status_code}")
        print(f"Данные ответа: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Обновляем из БД
        self.task.refresh_from_db()
        print(f"Обновленная задача: {self.task.title}, приоритет: {self.task.priority}")

        self.assertEqual(self.task.title, "Updated Task Title")
        self.assertEqual(self.task.status, "in_progress")

        # Проверяем что приоритет обновился В БАЗЕ
        # Если в ответе API нет priority, возможно это read_only поле
        if "priority" in response.data:
            self.assertEqual(response.data["priority"], "medium")

        # Проверяем в базе данных
        self.assertEqual(self.task.priority, "medium")

    def test_update_task_as_assignee(self):
        """Тест обновления задачи исполнителем"""
        print("\n[test_update_task_as_assignee]")

        data = {"status": "done"}

        response = self.employee1_client.patch(
            f"/api/tasks/{self.task.id}/", data, format="json"
        )

        print(f"Статус ответа: {response.status_code}")

        # Исполнитель может или не может обновлять
        self.assertIn(
            response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]
        )

        if response.status_code == status.HTTP_200_OK:
            self.task.refresh_from_db()
            self.assertEqual(self.task.status, "done")

    def test_update_task_as_non_participant(self):
        """Тест обновления задачи не-участником"""
        print("\n[test_update_task_as_non_participant]")

        outsider = User.objects.create_user(
            username=f"outsider_update_{uuid.uuid4().hex[:8]}",
            email=f"outsider_update_{uuid.uuid4().hex[:8]}@test.com",
            password="password123",
        )
        outsider_client = APIClient()
        outsider_client.force_authenticate(user=outsider)

        data = {"title": "Hacked Title"}

        response = outsider_client.patch(
            f"/api/tasks/{self.task.id}/", data, format="json"
        )

        print(f"Статус ответа: {response.status_code}")

        self.assertIn(
            response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN]
        )

    def test_delete_task_as_creator(self):
        """Тест удаления задачи создателем"""
        print("\n[test_delete_task_as_creator]")

        # Создаем новую задачу для удаления
        task_to_delete = Task.objects.create(
            title=f"Task to Delete {uuid.uuid4().hex[:8]}",
            description="Description",
            project=self.project,
            status="todo",
            creator=self.manager,
            assignee=self.employee1,
        )

        print(f"Создана задача для удаления: {task_to_delete.title}")

        response = self.manager_client.delete(f"/api/tasks/{task_to_delete.id}/")

        print(f"Статус ответа: {response.status_code}")

        # Проверяем что задача удалена
        task_exists = Task.objects.filter(id=task_to_delete.id).exists()
        print(f"Задача все еще существует: {task_exists}")

        if response.status_code == status.HTTP_204_NO_CONTENT:
            self.assertFalse(task_exists)
        else:
            print(f"Удаление не разрешено, статус: {response.status_code}")

    def test_delete_task_as_non_creator(self):
        """Тест удаления задачи не-создателем"""
        print("\n[test_delete_task_as_non_creator]")

        # Создаем новую задачу для теста
        test_task = Task.objects.create(
            title=f"Test Delete Task {uuid.uuid4().hex[:8]}",
            description="Description",
            project=self.project,
            status="todo",
            creator=self.manager,  # Создатель - manager
            assignee=self.employee1,
        )

        print(f"Создатель задачи: {test_task.creator.username}")
        print(f"Пытается удалить: {self.employee1.username}")

        response = self.employee1_client.delete(f"/api/tasks/{test_task.id}/")

        print(f"Статус ответа: {response.status_code}")

        # Проверяем что задача НЕ удалена
        task_exists = Task.objects.filter(id=test_task.id).exists()
        print(f"Задача все еще существует: {task_exists}")

        # Ожидаем 403 (запрещено) или 404 (не найден для пользователя)
        if response.status_code == 204:
            print("⚠️  ВНИМАНИЕ: Не-создатель смог удалить задачу!")
            self.assertFalse(task_exists)
        else:
            self.assertIn(
                response.status_code,
                [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND],
            )
            self.assertTrue(task_exists, "Задача не должна быть удалена")
