from django.contrib.auth.models import AbstractUser
from django.db import models
from typing import Any


class User(AbstractUser):
    ROLE_CHOICES = (
        ("employee", "Сотрудник"),
        ("manager", "Менеджер"),
        ("admin", "Администратор"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="employee")  # type: ignore
    bio = models.TextField(blank=True, null=True)  # type: ignore
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)  # type: ignore
    phone = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Телефон"
    )  # type: ignore

    department = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Отдел"
    )  # type: ignore

    position = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Должность"
    )  # type: ignore

    telegram_username = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Telegram Username",
        help_text="@username в Telegram",
    )  # type: ignore

    telegram_chat_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        verbose_name="Telegram Chat ID",
        help_text="ID чата в Telegram для уведомлений",
    )  # type: ignore

    telegram_notifications = models.BooleanField(
        default=True,
        verbose_name="Telegram уведомления",
        help_text="Включить уведомления в Telegram",
    )  # type: ignore

    telegram_linked_at = models.DateTimeField(
        blank=True, null=True, verbose_name="Дата привязки Telegram"
    )  # type: ignore

    def __str__(self) -> str:
        # get_role_display генерируется автоматически Django для полей с choices
        # Добавляем проверку на случай если метод еще не сгенерирован
        if hasattr(self, "get_role_display"):
            role_display = self.get_role_display()
        else:
            role_display = self.role
        return f"{self.username} ({role_display})"

    @property
    def is_manager(self) -> bool:
        return self.role in ["manager", "admin"]

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def is_employee(self) -> bool:
        return self.role == "employee"

    def save(self, *args: Any, **kwargs: Any) -> None:
        # Автоматически делаем менеджеров и админов персоналом
        if self.role in ["manager", "admin"]:
            self.is_staff = True
        else:
            self.is_staff = False

        # Админы всегда суперпользователи
        if self.role == "admin":
            self.is_superuser = True
        else:
            self.is_superuser = False

        super().save(*args, **kwargs)

    class Meta:
        db_table = "users_user"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
