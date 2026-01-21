# mypy: disable-error-code=attr-defined
from django.db import models
from typing import TYPE_CHECKING

# Для аннотаций с обратными ссылками
if TYPE_CHECKING:
    from apps.users.models import User
    from apps.tasks.models import Task


class Project(models.Model):
    """Модель проекта."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Активный"
        ON_HOLD = "on_hold", "На паузе"
        COMPLETED = "completed", "Завершён"
        ARCHIVED = "archived", "В архиве"

    # Аннотации типов для полей модели
    name = models.CharField(max_length=200, verbose_name="Название проекта")  # type: ignore
    description = models.TextField(blank=True, verbose_name="Описание")  # type: ignore
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Статус",
    )  # type: ignore
    creator = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="created_projects",
        verbose_name="Создатель",
    )  # type: ignore
    members = models.ManyToManyField(
        "users.User", related_name="projects", blank=True, verbose_name="Участники"
    )  # type: ignore
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")  # type: ignore
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")  # type: ignore

    @property
    def task_count(self) -> int:
        """Количество задач в проекте."""
        # Для TYPE_CHECKING указываем тип
        if TYPE_CHECKING:
            tasks: models.QuerySet[Task] = self.tasks  # type: ignore
            return tasks.count()
        return self.tasks.count()

    @property
    def completed_task_count(self) -> int:
        """Количество завершённых задач."""
        # Для TYPE_CHECKING указываем тип
        if TYPE_CHECKING:
            tasks: models.QuerySet[Task] = self.tasks  # type: ignore
            return tasks.filter(status="done").count()
        return self.tasks.filter(status="done").count()

    def get_members_display(self) -> str:
        """Отображает список участников."""
        return ", ".join([user.username for user in self.members.all()])

    # Добавляем аннотацию типа для атрибута short_description
    get_members_display.short_description = "Участники"  # type: ignore[attr-defined]

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name
