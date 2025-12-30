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

    class Meta:
        db_table = "users_user"
