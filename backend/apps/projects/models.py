from django.db import models


class Project(models.Model):
    """Модель проекта."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Активный"
        ON_HOLD = "on_hold", "На паузе"
        COMPLETED = "completed", "Завершён"
        ARCHIVED = "archived", "В архиве"

    name = models.CharField(max_length=200, verbose_name="Название проекта")
    description = models.TextField(blank=True, verbose_name="Описание")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Статус",
    )
    creator = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="created_projects",
        verbose_name="Создатель",
    )
    members = models.ManyToManyField(
        "users.User", related_name="projects", blank=True, verbose_name="Участники"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    @property
    def task_count(self):
        """Количество задач в проекте."""
        return self.tasks.count()

    @property
    def completed_task_count(self):
        """Количество завершённых задач."""
        return self.tasks.filter(status="done").count()

    def get_members_display(self):
        """Отображает список участников."""
        return ", ".join([user.username for user in self.members.all()])

    get_members_display.short_description = "Участники"

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
