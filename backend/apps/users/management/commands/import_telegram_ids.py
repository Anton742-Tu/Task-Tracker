import csv
from django.core.management.base import BaseCommand
from apps.users.models import User


class Command(BaseCommand):
    help = "Импорт Telegram chat_id из CSV файла"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Путь к CSV файлу")

    def handle(self, *args, **options):
        csv_file = options["csv_file"]

        with open(csv_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                email = row.get("email")
                chat_id = row.get("telegram_chat_id")

                if email and chat_id:
                    try:
                        user = User.objects.get(email=email)
                        user.telegram_chat_id = chat_id
                        user.save()
                        self.stdout.write(
                            self.style.SUCCESS(f"✅ {user.username}: chat_id добавлен")
                        )
                    except User.DoesNotExist:
                        self.stdout.write(
                            self.style.ERROR(f"❌ Пользователь не найден: {email}")
                        )
