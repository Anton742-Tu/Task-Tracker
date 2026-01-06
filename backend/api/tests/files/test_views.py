import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, TransactionTestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.files.models import FileAttachment
from apps.projects.models import Project
from apps.tasks.models import Task

User = get_user_model()


class FileAPITestCase(TransactionTestCase):
    """Тесты для API файлов"""

    def setUp(self):
        """Настройка тестовых данных"""
        # Создаем пользователей
        self.admin_user = User.objects.create_user(
            username="admin_test",
            email="admin@test.com",
            password="testpass123",
            role="admin",
            is_staff=True,
        )

        self.manager_user = User.objects.create_user(
            username="manager_test",
            email="manager@test.com",
            password="testpass123",
            role="manager",
        )

        self.employee_user = User.objects.create_user(
            username="employee_test",
            email="employee@test.com",
            password="testpass123",
            role="employee",
        )

        # Создаем проект
        self.project = Project.objects.create(
            name="Тестовый проект",
            description="Описание тестового проекта",
            status="active",
            creator=self.manager_user,
        )
        self.project.members.add(self.manager_user, self.employee_user)

        # Создаем задачу
        self.task = Task.objects.create(
            title="Тестовая задача",
            description="Описание тестовой задачи",
            project=self.project,
            status="todo",
            creator=self.manager_user,
        )

        # Создаем тестовые файлы
        self.test_image = SimpleUploadedFile(
            name="test_image.jpg",
            content=b"test image content",
            content_type="image/jpeg",
        )

        self.test_pdf = SimpleUploadedFile(
            name="test_document.pdf",
            content=b"test pdf content",
            content_type="application/pdf",
        )

        # Создаем API клиенты
        self.admin_client = APIClient()
        self.admin_client.force_authenticate(user=self.admin_user)

        self.manager_client = APIClient()
        self.manager_client.force_authenticate(user=self.manager_user)

        self.employee_client = APIClient()
        self.employee_client.force_authenticate(user=self.employee_user)

        self.anonymous_client = APIClient()

    def test_file_upload_as_manager(self):
        """Тест загрузки файла менеджером"""
        response = self.manager_client.post(
            "/api/files/upload/",
            {
                "file": self.test_image,
                "project_id": self.project.id,
                "description": "Тестовое изображение",
                "is_public": True,
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("file", response.data)
        self.assertEqual(response.data["file"]["description"], "Тестовое изображение")
        self.assertTrue(response.data["file"]["is_public"])
        self.assertEqual(response.data["file"]["file_type"], "document")

    def test_file_upload_as_employee_without_permission(self):
        """Тест загрузки файла сотрудником (без прав)"""
        response = self.employee_client.post(
            "/api/files/upload/",
            {
                "file": self.test_image,
                "project_id": self.project.id,
                "description": "Тестовое изображение",
            },
            format="multipart",
        )

        # Сотрудник может загружать файлы в свои проекты
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_file_upload_invalid_type(self):
        """Тест загрузки файла неверного типа"""
        # Используем .php файл - обычно запрещен
        invalid_file = SimpleUploadedFile(
            name="test.php",
            content=b"<?php system('rm -rf /'); ?>",  # Опасный PHP код
            content_type="application/x-httpd-php",
        )

        response = self.admin_client.post(
            "/api/files/upload/",
            {"file": invalid_file, "project_id": self.project.id},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("file", response.data)

    def test_file_upload_too_large(self):
        """Тест загрузки слишком большого файла"""
        # Создаем большой файл (11MB)
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        large_file = SimpleUploadedFile(
            name="large_file.jpg", content=large_content, content_type="image/jpeg"
        )

        response = self.admin_client.post(
            "/api/files/upload/",
            {"file": large_file, "project_id": self.project.id},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_file_list_as_admin(self):
        """Тест получения списка файлов администратором"""
        # Создаем несколько тестовых файлов
        for i in range(3):
            FileAttachment.objects.create(
                file=self.test_image,
                original_filename=f"test_{i}.jpg",
                file_type="image",
                mime_type="image/jpeg",
                file_size=1000,
                project=self.project,
                uploaded_by=self.admin_user,
                is_public=(i % 2 == 0),
            )

        response = self.admin_client.get("/api/files/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 3)

    def test_file_update_as_non_owner(self):
        """Тест обновления файла не-владельцем"""
        file_attachment = FileAttachment.objects.create(
            file=self.test_image,
            original_filename="test.jpg",
            file_type="image",
            mime_type="image/jpeg",
            file_size=1000,
            project=self.project,
            uploaded_by=self.manager_user,
        )

        update_data = {"description": "Попытка изменить чужой файл"}

        # Сотрудник пытается изменить файл менеджера
        response = self.employee_client.patch(
            f"/api/files/{file_attachment.id}/", data=update_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_file_download_as_unauthorized(self):
        """Тест скачивания файла без прав доступа"""
        file_attachment = FileAttachment.objects.create(
            file=self.test_image,
            original_filename="test.jpg",
            file_type="image",
            mime_type="image/jpeg",
            file_size=1000,
            project=self.project,
            uploaded_by=self.manager_user,
            is_public=False,  # Приватный файл
        )

        # Создаем пользователя не из проекта
        outsider = User.objects.create_user(
            username="outsider", email="outsider@test.com", password="testpass123"
        )

        outsider_client = APIClient()
        outsider_client.force_authenticate(user=outsider)

        response = outsider_client.get(f"/api/files/{file_attachment.id}/download/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_storage_stats_as_non_admin(self):
        """Тест получения статистики хранилища не-администратором"""
        response = self.manager_client.get("/api/files/stats/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authentication_required(self):
        """Тест что требуется аутентификация"""
        response = self.anonymous_client.get("/api/files/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
