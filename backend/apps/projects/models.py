from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Project(models.Model):
    """Модель проекта."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Активный"
        ON_HOLD = "on_hold", "На паузе"
        COMPLETED = "completed", "Завершён"
        ARCHIVED = "archived", "В архиве"

    name: str = models.CharField(max_length=200, verbose_name="Название проекта")
    description: str = models.TextField(blank=True, verbose_name="Описание")
    status: str = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Статус",
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_projects",
        verbose_name="Создатель",
    )
    members = models.ManyToManyField(
        User, related_name="projects", blank=True, verbose_name="Участники"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name
