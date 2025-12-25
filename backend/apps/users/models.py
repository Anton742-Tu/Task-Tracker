from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model."""

    ROLE_CHOICES = [
        ("employee", "Сотрудник"),
        ("manager", "Менеджер"),
        ("admin", "Администратор"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="employee", verbose_name="Роль")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    department = models.CharField(max_length=100, blank=True, verbose_name="Отдел")
    position = models.CharField(max_length=100, blank=True, verbose_name="Должность")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"

    @property
    def is_manager(self):
        return self.role in ["manager", "admin"]

    @property
    def is_admin(self):
        return self.role == "admin"
