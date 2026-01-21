import mimetypes
import os
from pathlib import Path

import filetype
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = get_user_model()


def validate_file_type(value):
    """Валидатор для проверки типа файла с использованием filetype"""
    # Читаем начало файла
    value.seek(0)
    file_content = value.read(1024)
    value.seek(0)  # Возвращаемся в начало файла

    # Используем filetype для определения реального типа файла
    try:
        kind = filetype.guess(file_content)
        if kind:
            mime = kind.mime
        else:
            # Если filetype не определил, используем расширение
            mime = mimetypes.guess_type(value.name)[0]
    except Exception:
        # Если ошибка, используем расширение
        mime = mimetypes.guess_type(value.name)[0]

    if not mime:
        raise ValidationError(_("Не удалось определить тип файла"))

    # Проверяем разрешенные типы
    if mime not in settings.ALLOWED_FILE_TYPES:
        raise ValidationError(
            _("Тип файла %(type)s не поддерживается") % {"type": mime}
        )


def validate_file_size(value):
    """Валидатор для проверки размера файла"""
    if value.size > settings.MAX_UPLOAD_SIZE:
        raise ValidationError(
            _("Размер файла не должен превышать %(size)d MB")
            % {"size": settings.MAX_UPLOAD_SIZE // (1024 * 1024)}
        )


def file_upload_path(instance, filename):
    """Генерация пути для загрузки файла"""
    # Определяем тип объекта для организации структуры папок
    if instance.user:
        folder = f"users/{instance.user.id}"
    elif instance.project:
        folder = f"projects/{instance.project.id}"
    elif instance.task:
        folder = f"tasks/{instance.task.id}"
    else:
        folder = "general"

    # Генерируем уникальное имя файла
    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    extension = Path(filename).suffix
    new_filename = f"{timestamp}_{Path(filename).stem}{extension}"

    return os.path.join("uploads", folder, new_filename)


class FileAttachment(models.Model):
    """Модель для хранения файлов и вложений"""

    FILE_TYPES = (
        ("image", "Изображение"),
        ("document", "Документ"),
        ("archive", "Архив"),
        ("other", "Другое"),
    )

    # Файл
    file = models.FileField(
        _("Файл"),
        upload_to=file_upload_path,
        validators=[validate_file_type, validate_file_size],
        max_length=500,
    )

    # Метаданные файла
    original_filename = models.CharField(_("Исходное имя файла"), max_length=255)
    file_type = models.CharField(_("Тип файла"), max_length=20, choices=FILE_TYPES)
    mime_type = models.CharField(_("MIME тип"), max_length=100)
    file_size = models.PositiveIntegerField(_("Размер файла (в байтах)"))

    # Связи с другими моделями
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="uploaded_files",
        verbose_name=_("Загружено пользователем"),
    )

    # ВАЖНО: используем названия в единственном числе
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="personal_files",
        null=True,
        blank=True,
        verbose_name=_("Пользователь (для персональных файлов)"),
    )

    project = models.ForeignKey(
        "projects.Project",  # Используем строковую ссылку
        on_delete=models.CASCADE,
        related_name="files",
        null=True,
        blank=True,
        verbose_name=_("Проект"),
    )

    task = models.ForeignKey(
        "tasks.Task",  # Используем строковую ссылку
        on_delete=models.CASCADE,
        related_name="files",
        null=True,
        blank=True,
        verbose_name=_("Задача"),
    )

    # Описание и метаданные
    description = models.TextField(_("Описание"), blank=True, default="")
    is_public = models.BooleanField(_("Публичный файл"), default=False)
    upload_date = models.DateTimeField(_("Дата загрузки"), auto_now_add=True)
    last_accessed = models.DateTimeField(_("Последний доступ"), null=True, blank=True)
    download_count = models.PositiveIntegerField(_("Количество скачиваний"), default=0)

    # Индексы для оптимизации запросов
    class Meta:
        verbose_name = _("Файл")
        verbose_name_plural = _("Файлы")
        ordering = ["-upload_date"]
        indexes = [
            models.Index(fields=["upload_date"]),
            models.Index(fields=["file_type"]),
            models.Index(fields=["is_public"]),
            models.Index(fields=["uploaded_by"]),
            models.Index(fields=["project"]),
            models.Index(fields=["task"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"{self.original_filename} ({self.get_file_type_display()})"

    def save(self, *args, **kwargs):
        """Переопределяем save для автоматического определения типа файла"""
        if not self.pk:  # Только при создании
            self._determine_file_metadata()

        super().save(*args, **kwargs)

    def _determine_file_metadata(self):
        """Определение метаданных файла (вынесено для уменьшения сложности)"""
        self._determine_mime_type()
        self._determine_file_category()
        self._set_filename_and_size()

    def _determine_mime_type(self):
        """Определение MIME типа с помощью filetype"""
        try:
            # Подготовка данных для filetype
            if hasattr(self.file, "file"):
                self.file.seek(0)
                file_content = self.file.read(1024)
                self.file.seek(0)
                kind = filetype.guess(file_content)
            else:
                self.file.seek(0)
                file_content = self.file.read(1024)
                self.file.seek(0)
                kind = filetype.guess(file_content)

            if kind:
                self.mime_type = kind.mime
                return
        except Exception as e:
            print(f"Error determining MIME type with filetype: {e}")

        # Fallback: используем расширение
        self.mime_type = self._get_mime_from_extension()

    def _get_mime_from_extension(self):
        """Получение MIME типа по расширению файла"""
        filename = None

        if hasattr(self, "original_filename") and self.original_filename:
            filename = self.original_filename
        elif hasattr(self.file, "name"):
            filename = self.file.name

        if filename:
            mime = mimetypes.guess_type(filename)[0]
            if mime:
                return mime

        return "application/octet-stream"

    def _determine_file_category(self):
        """Определение категории файла по MIME типу"""
        mime = self.mime_type

        # Список документов
        document_mimes = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/plain",
        ]

        # Список архивов
        archive_mimes = [
            "application/zip",
            "application/x-rar-compressed",
            "application/x-7z-compressed",
        ]

        if mime.startswith("image/"):
            self.file_type = "image"
        elif mime in document_mimes:
            self.file_type = "document"
        elif mime in archive_mimes:
            self.file_type = "archive"
        else:
            self.file_type = "other"

    def _set_filename_and_size(self):
        """Установка имени файла и размера"""
        # Имя файла
        if hasattr(self.file, "name"):
            self.original_filename = self.file.name.split("/")[-1]
        elif not hasattr(self, "original_filename") or not self.original_filename:
            self.original_filename = f"file_{timezone.now().strftime('%Y%m%d_%H%M%S')}"

        # Размер файла
        if hasattr(self.file, "size"):
            self.file_size = self.file.size
        elif not hasattr(self, "file_size") or not self.file_size:
            self.file_size = 0

    def delete(self, *args, **kwargs):
        """Удаляем физический файл при удалении записи"""
        if self.file:
            storage, path = self.file.storage, self.file.path
            super().delete(*args, **kwargs)
            try:
                storage.delete(path)
            except Exception:
                pass  # Игнорируем ошибки удаления файла
        else:
            super().delete(*args, **kwargs)

    @property
    def extension(self):
        """Возвращает расширение файла"""
        if self.original_filename:
            return Path(self.original_filename).suffix.lower()
        return ""

    @property
    def file_size_human(self):
        """Возвращает размер файла в человеко-читаемом формате"""
        size = self.file_size
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    @property
    def file_url(self):
        """Возвращает URL для доступа к файлу"""
        return self.file.url if self.file else None

    def increment_download_count(self):
        """Увеличивает счетчик скачиваний"""
        self.download_count += 1
        self.last_accessed = timezone.now()
        self.save(update_fields=["download_count", "last_accessed"])

    def can_access(self, user):
        """Проверяет, имеет ли пользователь доступ к файлу"""
        if self.is_public:
            return True

        if not user.is_authenticated:
            return False

        # Администратор имеет доступ ко всем файлам
        if user.role == "admin":
            return True

        # Владелец файла имеет доступ
        if self.uploaded_by == user:
            return True

        # Проверяем доступ через связанные объекты
        if self.user and self.user == user:
            return True

        if self.project and self.project.members.filter(id=user.id).exists():
            return True

        if self.task:
            # Проверяем доступ через задачу
            if self.task.assignee == user or self.task.creator == user:
                return True
            # Проверяем доступ через проект задачи
            if (
                self.task.project
                and self.task.project.members.filter(id=user.id).exists()
            ):
                return True

        return False
