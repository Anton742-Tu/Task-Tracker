from django.db import models


class Task(models.Model):
    """Модель задачи."""

    class Status(models.TextChoices):
        TODO = "todo", "К выполнению"
        IN_PROGRESS = "in_progress", "В работе"
        REVIEW = "review", "На проверке"
        DONE = "done", "Выполнена"
        BLOCKED = "blocked", "Заблокирована"

    class Priority(models.TextChoices):
        LOW = "low", "Низкий"
        MEDIUM = "medium", "Средний"
        HIGH = "high", "Высокий"
        CRITICAL = "critical", "Критический"

    title = models.CharField(max_length=200, verbose_name="Заголовок")  # type: ignore
    description = models.TextField(blank=True, verbose_name="Описание")  # type: ignore
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name="Проект",
    )  # type: ignore
    creator = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="created_tasks",
        verbose_name="Создатель",
        null=True,
        blank=True,
    )  # type: ignore
    assignee = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
        verbose_name="Исполнитель",
    )  # type: ignore
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
        verbose_name="Статус",
    )  # type: ignore
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name="Приоритет",
    )  # type: ignore
    due_date = models.DateField(null=True, blank=True, verbose_name="Срок выполнения")  # type: ignore
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")  # type: ignore
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")  # type: ignore

    @property
    def is_overdue(self) -> bool:
        """Проверяет, просрочена ли задача."""
        if self.due_date:
            from django.utils import timezone

            return self.status != "done" and self.due_date < timezone.now().date()
        return False

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ["-priority", "-created_at"]

    def __str__(self) -> str:
        return f"{self.title} ({self.get_status_display()})"  # type: ignore
