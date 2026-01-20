from django.core.management.base import BaseCommand
import requests
from django.conf import settings
from django.urls import reverse


class Command(BaseCommand):
    help = "Установить вебхук для Telegram бота"

    def handle(self, *args, **options):
        bot_token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
        site_url = getattr(settings, "SITE_URL", "http://localhost:8000")

        if not bot_token:
            self.stdout.write(self.style.ERROR("❌ TELEGRAM_BOT_TOKEN не настроен"))
            return

        # URL для вебхука
        webhook_url = f"{site_url}/api/telegram-webhook/"

        try:
            url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
            payload = {"url": webhook_url, "drop_pending_updates": True}

            response = requests.post(url, json=payload, timeout=10)
            data = response.json()

            if data.get("ok"):
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Webhook установлен: {webhook_url}")
                )
                self.stdout.write(f"📝 Описание: {data.get('description', '')}")
            else:
                self.stdout.write(self.style.ERROR(f"❌ Ошибка: {data}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Ошибка установки webhook: {e}"))
