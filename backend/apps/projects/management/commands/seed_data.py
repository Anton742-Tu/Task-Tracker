from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Заполняет базу данных тестовыми данными"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # Создаем пользователей
        admin_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        admin_user.set_password("admin123")
        admin_user.save()

        manager, _ = User.objects.get_or_create(
            username="manager",
            defaults={
                "email": "manager@example.com",
                "first_name": "Иван",
                "last_name": "Менеджеров",
            },
        )
        manager.set_password("manager123")
        manager.save()

        # ... остальной код из fixtures/sample_data.py

        self.stdout.write(self.style.SUCCESS("Тестовые данные успешно созданы!"))
        self.stdout.write("Доступные пользователи:")
        self.stdout.write("- admin / admin123 (администратор)")
        self.stdout.write("- manager / manager123 (менеджер)")
