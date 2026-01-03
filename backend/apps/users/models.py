from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ("employee", "Сотрудник"),
        ("manager", "Менеджер"),
        ("admin", "Администратор"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="employee")
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_manager(self):
        return self.role in ["manager", "admin"]

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_employee(self):
        return self.role == self.Role.EMPLOYEE

    def save(self, *args, **kwargs):
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
