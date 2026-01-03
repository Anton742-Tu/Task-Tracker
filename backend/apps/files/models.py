import os

import magic
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


def upload_to(instance, filename):
    """Генерируем путь для загрузки файла"""
    now = timezone.now()

    # Определяем тип контента (задача, проект, пользователь)
    if instance.task:
        folder = f"tasks/{instance.task.id}"
    elif instance.project:
        folder = f"projects/{instance.project.id}"
    elif instance.user:
        folder = f"users/{instance.user.id}"
    else:
        folder = "general"

    # Добавляем дату для организации
    date_path = now.strftime("%Y/%m/%d")

    # Сохраняем оригинальное имя, но с slugify для безопасности
    name, ext = os.path.splitext(filename)
    safe_name = slugify(name)[:50]  # Ограничиваем длину
    filename = f"{safe_name}{ext}"

    return f"uploads/{folder}/{date_path}/{filename}"


class FileAttachment(models.Model):
    """Модель для хранения файловых вложений"""

    class FileType(models.TextChoices):
        DOCUMENT = "document", "Документ"
        IMAGE = "image", "Изображение"
        ARCHIVE = "archive", "Архив"
        AUDIO = "audio", "Аудио"
        VIDEO = "video", "Видео"
        OTHER = "other", "Другое"

    # Основные поля
    file = models.FileField(upload_to=upload_to, verbose_name="Файл", max_length=500)

    original_filename = models.CharField(
        max_length=255, verbose_name="Оригинальное имя файла"
    )

    file_type = models.CharField(
        max_length=20, choices=FileType.choices, verbose_name="Тип файла"
    )

    mime_type = models.CharField(max_length=100, verbose_name="MIME тип", blank=True)

    file_size = models.PositiveIntegerField(
        verbose_name="Размер файла (байты)", default=0
    )

    # Связи с другими моделями
    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.CASCADE,
        related_name="attachments",
        null=True,
        blank=True,
        verbose_name="Задача",
    )

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="attachments",
        null=True,
        blank=True,
        verbose_name="Проект",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="attachments",
        null=True,
        blank=True,
        verbose_name="Пользователь",
    )

    # Метаданные
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="uploaded_files",
        null=True,
        verbose_name="Загрузил",
    )

    description = models.TextField(verbose_name="Описание", blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")

    is_public = models.BooleanField(default=False, verbose_name="Публичный доступ")

    # Методы
    def save(self, *args, **kwargs):
        """Переопределяем save для определения типа файла"""
        if self.file and not self.original_filename:
            self.original_filename = os.path.basename(self.file.name)

        if self.file and not self.file_size:
            try:
                self.file_size = self.file.size
            except (ValueError, OSError):
                self.file_size = 0

        if self.file and not self.mime_type:
            try:
                # Используем python-magic для определения MIME типа
                mime = magic.Magic(mime=True)
                self.mime_type = mime.from_buffer(self.file.read(1024))
                self.file.seek(0)  # Возвращаем указатель файла
            except Exception:
                # Fallback: определяем по расширению
                ext = os.path.splitext(self.original_filename)[1].lower()
                self.mime_type = self._get_mime_by_extension(ext)

        if self.file and not self.file_type:
            self.file_type = self._determine_file_type()

        super().save(*args, **kwargs)

    def _determine_file_type(self):
        """Определяем тип файла по MIME типу"""
        if not self.mime_type:
            return self.FileType.OTHER

        mime = self.mime_type.lower()

        if mime.startswith("image/"):
            return self.FileType.IMAGE
        elif mime.startswith("video/"):
            return self.FileType.VIDEO
        elif mime.startswith("audio/"):
            return self.FileType.AUDIO
        elif mime in [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/plain",
            "text/html",
            "application/json",
        ]:
            return self.FileType.DOCUMENT
        elif mime in [
            "application/zip",
            "application/x-rar-compressed",
            "application/x-tar",
            "application/x-7z-compressed",
        ]:
            return self.FileType.ARCHIVE
        else:
            return self.FileType.OTHER

    def _get_mime_by_extension(self, ext):
        """Определяем MIME тип по расширению"""
        mime_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xls": "application/vnd.ms-excel",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".txt": "text/plain",
            ".zip": "application/zip",
            ".rar": "application/x-rar-compressed",
        }
        return mime_map.get(ext, "application/octet-stream")

    @property
    def file_size_human(self):
        """Человекочитаемый размер файла"""
        size = self.file_size
        for unit in ["Б", "КБ", "МБ", "ГБ"]:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} ТБ"

    @property
    def extension(self):
        """Расширение файла"""
        return os.path.splitext(self.original_filename)[1].lower()

    @property
    def is_image(self):
        """Является ли файл изображением"""
        return self.file_type == self.FileType.IMAGE

    @property
    def is_document(self):
        """Является ли файл документом"""
        return self.file_type == self.FileType.DOCUMENT

    def delete(self, *args, **kwargs):
        """Удаляем файл с диска при удалении записи"""
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.original_filename} ({self.file_size_human})"

    class Meta:
        verbose_name = "Файловое вложение"
        verbose_name_plural = "Файловые вложения"
        ordering = ["-uploaded_at"]
        indexes = [
            models.Index(fields=["file_type"]),
            models.Index(fields=["uploaded_at"]),
            models.Index(fields=["task", "project", "user"]),
        ]
