from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя."""

    ROLE_CHOICES = [
        ("employee", "Сотрудник"),
        ("manager", "Менеджер"),
        ("admin", "Администратор"),
    ]

    role: str = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default="employee", verbose_name="Роль"
    )
    phone: str = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    department: str = models.CharField(max_length=100, blank=True, verbose_name="Отдел")
    position: str = models.CharField(
        max_length=100, blank=True, verbose_name="Должность"
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        return f"{self.get_full_name() or self.username} ({self.role})"

    @property
    def is_manager(self) -> bool:
        return self.role in ["manager", "admin"]

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"
