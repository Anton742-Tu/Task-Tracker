from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from api.serializers.files import (FileAttachmentSerializer,
                                   FileUpdateSerializer, FileUploadSerializer)
from apps.files.models import FileAttachment
from apps.projects.models import Project
from apps.tasks.models import Task

User = get_user_model()


class FileSerializerTestCase(TestCase):
    """Тесты для сериализаторов файлов"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.project = Project.objects.create(
            name="Тестовый проект",
            description="Описание",
            status="active",
            creator=self.user,
        )

        self.task = Task.objects.create(
            title="Тестовая задача",
            description="Описание",
            project=self.project,
            status="todo",
        )

        self.test_file = SimpleUploadedFile(
            name="test.jpg", content=b"test content", content_type="image/jpeg"
        )

    def test_file_attachment_serializer(self):
        """Тест сериализатора FileAttachmentSerializer"""
        file_attachment = FileAttachment.objects.create(
            file=self.test_file,
            original_filename="test.jpg",
            file_type="image",
            mime_type="image/jpeg",
            file_size=1000,
            project=self.project,
            uploaded_by=self.user,
            description="Тестовый файл",
            is_public=True,
        )

        serializer = FileAttachmentSerializer(file_attachment)
        data = serializer.data

        self.assertEqual(data["original_filename"], "test.jpg")
        self.assertEqual(data["file_type"], "image")
        self.assertEqual(data["description"], "Тестовый файл")
        self.assertTrue(data["is_public"])
        self.assertIn("file_size_human", data)
        self.assertIn("extension", data)
        self.assertIn("uploaded_by_username", data)

    def test_file_upload_serializer_valid(self):
        """Тест валидного сериализатора загрузки файла"""
        data = {
            "file": self.test_file,
            "project_id": self.project.id,
            "description": "Тестовое описание",
            "is_public": True,
        }

        serializer = FileUploadSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        # Проверяем созданный объект
        file_attachment = serializer.save()
        self.assertEqual(file_attachment.description, "Тестовое описание")
        self.assertTrue(file_attachment.is_public)
        self.assertEqual(file_attachment.project, self.project)

    def test_file_upload_serializer_invalid_file_type(self):
        """Тест сериализатора с неверным типом файла"""
        invalid_file = SimpleUploadedFile(
            name="test.exe", content=b"evil", content_type="application/x-msdownload"
        )

        data = {"file": invalid_file, "project_id": self.project.id}

        serializer = FileUploadSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("file", serializer.errors)

    def test_file_upload_serializer_missing_attachment(self):
        """Тест сериализатора без привязки к объекту"""
        data = {"file": self.test_file}

        serializer = FileUploadSerializer(
            data=data,
            context={"request": type("obj", (object,), {"user": self.user})()},
        )
        self.assertTrue(serializer.is_valid())

        file_attachment = serializer.save()
        self.assertEqual(file_attachment.user, self.user)

    def test_file_upload_serializer_password_mismatch(self):
        """Тест сериализатора с несовпадающими паролями (если бы было)"""
        # Этот тест демонстрирует паттерн тестирования валидации
        pass

    def test_file_update_serializer(self):
        """Тест сериализатора обновления файла"""
        file_attachment = FileAttachment.objects.create(
            file=self.test_file,
            original_filename="test.jpg",
            file_type="image",
            mime_type="image/jpeg",
            file_size=1000,
            project=self.project,
            uploaded_by=self.user,
        )

        update_data = {"description": "Обновленное описание", "is_public": False}

        serializer = FileUpdateSerializer(
            file_attachment, data=update_data, partial=True
        )
        self.assertTrue(serializer.is_valid())

        updated = serializer.save()
        self.assertEqual(updated.description, "Обновленное описание")
        self.assertFalse(updated.is_public)
