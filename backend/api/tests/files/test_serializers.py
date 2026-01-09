import os
import sys

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

# from api.files.serializers import (FileAttachmentSerializer,
#                                   FileUpdateSerializer, FileUploadSerializer)
from apps.files.models import FileAttachment

User = get_user_model()

# Добавляем путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))


try:
    # Пробуем разные пути импорта
    from api.files.serializers import (FileAttachmentSerializer,
                                       FileUpdateSerializer,
                                       FileUploadSerializer)
except ImportError:
    try:
        from apps.files.serializers import (FileAttachmentSerializer,
                                            FileUpdateSerializer,
                                            FileUploadSerializer)
    except ImportError:
        # Создаем заглушки если не найдено
        print("⚠️  Сериализаторы файлов не найдены")
        FileAttachmentSerializer = None
        FileUploadSerializer = None
        FileUpdateSerializer = None
        raise


class FileSerializerTestCase(TestCase):
    """Тесты для сериализаторов файлов"""

    def setUp(self):
        """Настройка тестовых данных"""
        if FileAttachmentSerializer is None:
            self.skipTest("Сериализаторы файлов не найдены")

        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        from apps.projects.models import Project
        from apps.tasks.models import Task

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
            assignee=self.user,
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

        self.assertIn("upload_date", data)
        self.assertEqual(data["original_filename"], "test.jpg")
        self.test_file = SimpleUploadedFile(
            name="test.jpg", content=b"test content", content_type="image/jpeg"
        )
        self.assertEqual(data["description"], "Тестовый файл")
        self.assertTrue(data["is_public"])

    def test_file_upload_serializer_valid(self):
        """Тест валидного сериализатора загрузки файла"""
        context = {"request": type("obj", (), {"user": self.user})()}

        data = {
            "file": self.test_file,
            "project_id": self.project.id,
            "description": "Тестовое описание",
            "is_public": True,
        }

        serializer = FileUploadSerializer(data=data, context=context)
        self.assertTrue(serializer.is_valid())

        # Проверяем созданный объект
        file_attachment = serializer.save()
        self.assertEqual(file_attachment.description, "Тестовое описание")
        self.assertTrue(file_attachment.is_public)
        self.assertEqual(file_attachment.project, self.project)
        self.assertEqual(file_attachment.uploaded_by, self.user)

    def test_file_upload_serializer_invalid_file_type(self):
        """Тест сериализатора с неверным типом файла"""
        invalid_file = SimpleUploadedFile(
            name="test.bat",  # .bat файлы обычно запрещены
            content=b"@echo off\ndel *.*",  # опасный контент
            content_type="application/x-msdownload",  # или другой запрещенный тип
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
