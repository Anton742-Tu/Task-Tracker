# apps/tasks/management/commands/test_telegram.py
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.tasks.signals import send_telegram_message


class Command(BaseCommand):
    help = "Тестирование Telegram бота"

    def add_arguments(self, parser):
        parser.add_argument(
            "--message",
            type=str,
            default="Тестовое сообщение от бота!",
            help="Сообщение для отправки",
        )

    def handle(self, *args, **options):
        message = options["message"]
        telegram_chat_ids = getattr(settings, "TELEGRAM_CHAT_IDS", {})

        if not telegram_chat_ids:
            self.stdout.write(self.style.ERROR("❌ TELEGRAM_CHAT_IDS не настроены"))
            return

        self.stdout.write(f"📤 Отправка сообщения: '{message}'")

        for name, chat_id in telegram_chat_ids.items():
            self.stdout.write(f"\n👉 Отправка {name} (ID: {chat_id})...")

            success = send_telegram_message(
                chat_id, f"🤖 <b>Тестирование бота</b>\n\n{message}"
            )

            if success:
                self.stdout.write(self.style.SUCCESS("✅ Отправлено успешно"))
            else:
                self.stdout.write(self.style.ERROR("❌ Ошибка отправки"))
