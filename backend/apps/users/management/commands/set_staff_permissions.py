from django.core.management.base import BaseCommand

from apps.users.models import User


class Command(BaseCommand):
    help = "Назначить права персонала менеджерам и администраторам"

    def handle(self, *args, **kwargs):
        # Обновляем менеджеров
        managers = User.objects.filter(role="manager")
        managers.update(is_staff=True)
        self.stdout.write(f"Назначены права персонала {managers.count()} менеджерам")

        # Обновляем администраторов
        admins = User.objects.filter(role="admin")
        admins.update(is_staff=True, is_superuser=True)
        self.stdout.write(
            f"Назначены права администратора {admins.count()} пользователям"
        )

        self.stdout.write(self.style.SUCCESS("Права успешно назначены!"))
