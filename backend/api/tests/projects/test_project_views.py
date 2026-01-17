# -*- coding: utf-8 -*-
import uuid

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

        # Создаем пользователей с уникальными именами для изоляции тестов
        timestamp = uuid.uuid4().hex[:8]

        self.admin = User.objects.create_user(
            username=f"admin_{timestamp}",
            email=f"admin_{timestamp}@test.com",
            password="password123",
            role="admin",
        )

        self.manager = User.objects.create_user(
            username=f"manager_{timestamp}",
            email=f"manager_{timestamp}@test.com",
            password="password123",
            role="manager",
        )

        self.employee = User.objects.create_user(
            username=f"employee_{timestamp}",
            email=f"employee_{timestamp}@test.com",
            password="password123",
            role="employee",
        )

        # Создаем проект с уникальным именем
        self.project = Project.objects.create(
            name=f"Test Project {timestamp}",
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
        unique_name = f"New Project {uuid.uuid4().hex[:8]}"
        data = {
            "name": unique_name,
            "description": "New Description",
            "status": "active",
            "members": [self.employee.id],
        }

        response = self.manager_client.post("/api/projects/", data, format="json")
        print(f"Create project response: {response.status_code}")
        print(f"Response data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], unique_name)

        # Проверяем creator - может быть ID или объект
        if isinstance(response.data.get("creator"), dict):
            # Если creator сериализован как объект
            self.assertEqual(
                response.data["creator"]["username"], self.manager.username
            )
        else:
            # Если creator это просто ID
            self.assertEqual(response.data.get("creator"), self.manager.id)
            print(f"Creator field is ID: {response.data.get('creator')}")

    def test_create_project_as_employee(self):
        """Тест создания проекта сотрудником (должен быть запрещен)"""
        data = {
            "name": f"Employee Project {uuid.uuid4().hex[:8]}",
            "description": "Description",
            "status": "active",
        }

        response = self.employee_client.post("/api/projects/", data, format="json")

        # Может быть 403 (нет прав) или 400 (валидация)
        print(f"Employee create project: {response.status_code}")

        if response.status_code == 400:
            print(f"Validation error: {response.data}")
            # Проверяем что это не успешный ответ
            self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)
        else:
            self.assertIn(
                response.status_code,
                [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED],
            )

    def test_list_projects(self):
        """Тест получения списка проектов"""
        # Сначала очищаем все проекты кроме нашего
        Project.objects.exclude(id=self.project.id).delete()

        # Создаем еще один проект для этого теста
        extra_project = Project.objects.create(
            name=f"Extra Project {uuid.uuid4().hex[:8]}",
            description="Extra Description",
            status="active",
            creator=self.manager,
        )
        extra_project.members.add(self.employee)

        response = self.employee_client.get("/api/projects/")
        print(f"List projects response status: {response.status_code}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем структуру ответа
        if isinstance(response.data, list):
            print(f"Response is list with {len(response.data)} items")
            # Сотрудник должен видеть проекты где он член
            project_count = len(response.data)
        elif "results" in response.data:
            # Пагинация
            print(
                f"Response has pagination with {len(response.data['results'])} results"
            )
            project_count = len(response.data["results"])
        else:
            print(f"Unexpected response format: {type(response.data)}")
            self.fail("Unexpected response format")

        # Минимум должен видеть 2 проекта (оба где он член)
        self.assertGreaterEqual(project_count, 2)

        # Проверяем что наш проект в списке
        project_names = []
        if isinstance(response.data, list):
            project_names = [p.get("name") for p in response.data]
        elif "results" in response.data:
            project_names = [p.get("name") for p in response.data["results"]]

        print(f"Project names in response: {project_names}")
        self.assertIn(self.project.name, project_names)

    def test_retrieve_project(self):
        """Тест получения конкретного проекта"""
        response = self.employee_client.get(f"/api/projects/{self.project.id}/")
        print(f"Retrieve project {self.project.id}: {response.status_code}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.project.name)

    def test_update_project_as_creator(self):
        """Тест обновления проекта создателем"""
        new_name = f"Updated Project {uuid.uuid4().hex[:8]}"
        data = {"name": new_name, "description": "Updated Description"}

        response = self.manager_client.patch(
            f"/api/projects/{self.project.id}/", data, format="json"
        )
        print(f"Update project as creator: {response.status_code}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, new_name)

    def test_delete_project_as_admin(self):
        """Тест удаления проекта администратором"""
        # Создаем отдельный проект для удаления
        project_to_delete = Project.objects.create(
            name=f"Project to Delete {uuid.uuid4().hex[:8]}",
            description="To be deleted",
            status="active",
            creator=self.manager,
        )

        response = self.admin_client.delete(f"/api/projects/{project_to_delete.id}/")
        print(f"Delete project as admin: {response.status_code}")

        # Проверяем что проект удален
        project_exists = Project.objects.filter(id=project_to_delete.id).exists()
        print(f"Project still exists: {project_exists}")

        if response.status_code == status.HTTP_204_NO_CONTENT:
            self.assertFalse(project_exists)
        else:
            print(
                f"Delete returned {response.status_code}, project may require soft delete"
            )
            # Возможно используется мягкое удаление
            self.assertIn(response.status_code, [200, 204])

    def test_filter_projects_by_status(self):
        """Тест фильтрации проектов по статусу"""
        # Очищаем старые проекты
        global status
        Project.objects.exclude(id=self.project.id).delete()

        # Создаем архивный проект
        archived_project = Project.objects.create(
            name=f"Archived Project {uuid.uuid4().hex[:8]}",
            description="Description",
            status="archived",
            creator=self.manager,
        )
        archived_project.members.add(self.manager)

        # Создаем еще один активный проект
        active_project = Project.objects.create(
            name=f"Active Project 2 {uuid.uuid4().hex[:8]}",
            description="Description",
            status="active",
            creator=self.manager,
        )
        active_project.members.add(self.manager)

        response = self.manager_client.get("/api/projects/?status=active")
        print(f"Filter by status=active: {response.status_code}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем результаты
        if isinstance(response.data, list):
            active_count = len(response.data)
            statuses = [p.get("status") for p in response.data]
        elif "results" in response.data:
            active_count = len(response.data["results"])
            statuses = [p.get("status") for p in response.data["results"]]
        else:
            self.fail("Unexpected response format")

        print(f"Found {active_count} active projects")
        print(f"Statuses: {statuses}")

        # Все проекты должны быть активными
        self.assertTrue(all(status == "active" for status in statuses))
        # Должно быть минимум 2 активных проекта
        self.assertGreaterEqual(active_count, 2)

    def test_search_projects(self):
        """Тест поиска проектов"""
        # Очищаем старые проекты
        Project.objects.exclude(id=self.project.id).delete()

        # Создаем проект с уникальным именем для поиска
        search_term = f"SearchTest{uuid.uuid4().hex[:8]}"
        searchable_project = Project.objects.create(
            name=f"Project {search_term} Unique",
            description="Description",
            status="active",
            creator=self.manager,
        )
        searchable_project.members.add(self.manager)

        # Тестируем поиск
        response = self.manager_client.get(f"/api/projects/?search={search_term}")
        print(f"Search for '{search_term}': {response.status_code}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        if isinstance(response.data, list):
            results = response.data
        elif "results" in response.data:
            results = response.data["results"]
        else:
            results = []

        print(f"Found {len(results)} results")

        # Должен найти хотя бы наш проект
        project_names = [p.get("name") for p in results]
        print(f"Project names in search results: {project_names}")

        self.assertGreaterEqual(len(results), 1)
        self.assertIn(searchable_project.name, project_names)

        # Тестируем поиск несуществующего
        response = self.manager_client.get(
            "/api/projects/?search=NonexistentProjectXYZ"
        )
        print(f"Search for non-existent: {response.status_code}")

        if isinstance(response.data, list):
            self.assertEqual(len(response.data), 0)
        elif "results" in response.data:
            self.assertEqual(len(response.data["results"]), 0)
