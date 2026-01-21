# mypy: ignore-errors
import mimetypes
import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Any, Union, cast

import filetype
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files import File as DjangoFile
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from django.db.models.query import QuerySet
    from apps.projects.models import Project
    from apps.tasks.models import Task
    from apps.users.models import User as UserModel

    UserType = UserModel
else:
    UserType = get_user_model()


def validate_file_type(value: DjangoFile) -> None:
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
            filename = value.name if value.name else ""
            mime = mimetypes.guess_type(filename)[0]
    except Exception:
        # Если ошибка, используем расширение
        filename = value.name if value.name else ""
        mime = mimetypes.guess_type(filename)[0]

    if not mime:
        raise ValidationError(_("Не удалось определить тип файла"))

    # Проверяем разрешенные типы
    if mime not in settings.ALLOWED_FILE_TYPES:
        raise ValidationError(
            _("Тип файла %(type)s не поддерживается") % {"type": mime}
        )


def validate_file_size(value: DjangoFile) -> None:
    """Валидатор для проверки размера файла"""
    if value.size > settings.MAX_UPLOAD_SIZE:
        raise ValidationError(
            _("Размер файла не должно превышать %(size)d MB")
            % {"size": settings.MAX_UPLOAD_SIZE // (1024 * 1024)}
        )


def file_upload_path(instance: "FileAttachment", filename: str) -> str:
    """Генерация пути для загрузки файла"""
    # Определяем тип объекта для организации структуры папок
    user = getattr(instance, "user", None)
    project = getattr(instance, "project", None)
    task = getattr(instance, "task", None)

    if user and hasattr(user, "id"):
        folder = f"users/{user.id}"
    elif project and hasattr(project, "id"):
        folder = f"projects/{project.id}"
    elif task and hasattr(task, "id"):
        folder = f"tasks/{task.id}"
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
        UserType,
        on_delete=models.CASCADE,
        related_name="uploaded_files",
        verbose_name=_("Загружено пользователем"),
    )

    # ВАЖНО: используем названия в единственном числе
    user = models.ForeignKey(
        UserType,
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

    def __str__(self) -> str:
        return f"{self.original_filename} ({self.get_file_type_display()})"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Переопределяем save для автоматического определения типа файла"""
        if not self.pk:  # Только при создании
            self._determine_file_metadata()

        super().save(*args, **kwargs)

    def _determine_file_metadata(self) -> None:
        """Определение метаданных файла (вынесено для уменьшения сложности)"""
        self._determine_mime_type()
        self._determine_file_category()
        self._set_filename_and_size()

    def _determine_mime_type(self) -> None:
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

    def _get_mime_from_extension(self) -> str:
        """Получение MIME типа по расширению файла"""
        filename: Optional[str] = None

        if hasattr(self, "original_filename") and self.original_filename:
            filename = self.original_filename
        elif hasattr(self.file, "name"):
            filename = str(self.file.name)

        if filename:
            mime = mimetypes.guess_type(filename)[0]
            if mime:
                return mime

        return "application/octet-stream"

    def _determine_file_category(self) -> None:
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

    def _set_filename_and_size(self) -> None:
        """Установка имени файла и размера"""
        # Имя файла
        if hasattr(self.file, "name"):
            self.original_filename = str(self.file.name).split("/")[-1]
        elif not hasattr(self, "original_filename") or not self.original_filename:
            self.original_filename = f"file_{timezone.now().strftime('%Y%m%d_%H%M%S')}"

        # Размер файла
        if hasattr(self.file, "size"):
            self.file_size = self.file.size
        elif not hasattr(self, "file_size") or not self.file_size:
            self.file_size = 0

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        """Удаляем физический файл при удалении записи"""
        if self.file:
            storage = self.file.storage
            path = self.file.path
            result = super().delete(*args, **kwargs)
            try:
                storage.delete(path)
            except Exception:
                pass  # Игнорируем ошибки удаления файла
            return result
        else:
            return super().delete(*args, **kwargs)

    @property
    def extension(self) -> str:
        """Возвращает расширение файла"""
        if self.original_filename:
            return Path(self.original_filename).suffix.lower()
        return ""

    @property
    def file_size_human(self) -> str:
        """Возвращает размер файла в человеко-читаемом формате"""
        size = float(self.file_size)  # Преобразуем к float для деления
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    @property
    def file_url(self) -> Optional[str]:
        """Возвращает URL для доступа к файлу"""
        return self.file.url if self.file else None

    def increment_download_count(self) -> None:
        """Увеличивает счетчик скачиваний"""
        self.download_count += 1
        self.last_accessed = timezone.now()
        self.save(update_fields=["download_count", "last_accessed"])

    def can_access(self, user: Any) -> bool:
        """Проверяет, имеет ли пользователь доступ к файлу"""
        if self.is_public:
            return True

        if not hasattr(user, "is_authenticated") or not user.is_authenticated:
            return False

        # Администратор имеет доступ ко всем файлам
        if hasattr(user, "role") and user.role == "admin":
            return True

        # Владелец файла имеет доступ
        if hasattr(user, "id") and hasattr(self.uploaded_by, "id"):
            if user.id == self.uploaded_by.id:
                return True

        # Проверяем доступ через связанные объекты
        if hasattr(user, "id") and self.user and hasattr(self.user, "id"):
            if user.id == self.user.id:
                return True

        if self.project and hasattr(user, "id"):
            # Для TYPE_CHECKING используем каст
            if TYPE_CHECKING:
                project = cast("Project", self.project)
                return project.members.filter(id=user.id).exists()
            else:
                return self.project.members.filter(id=user.id).exists()

        if self.task and hasattr(user, "id"):
            # Для TYPE_CHECKING используем каст
            if TYPE_CHECKING:
                task = cast("Task", self.task)
                if task.assignee and task.assignee.id == user.id:
                    return True
                if task.creator and task.creator.id == user.id:
                    return True
                if task.project and task.project.members.filter(id=user.id).exists():
                    return True
            else:
                if self.task.assignee and self.task.assignee.id == user.id:
                    return True
                if self.task.creator and self.task.creator.id == user.id:
                    return True
                if (
                    self.task.project
                    and self.task.project.members.filter(id=user.id).exists()
                ):
                    return True

        return False
