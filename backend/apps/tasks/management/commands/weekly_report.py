from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.tasks.models import Task
from apps.tasks.signals import send_telegram_message
from django.conf import settings


class Command(BaseCommand):
    help = "Еженедельный отчет по задачам"

    def handle(self, *args, **options):
        week_ago = timezone.now() - timedelta(days=7)

        # Статистика
        created_this_week = Task.objects.filter(created_at__gte=week_ago).count()
        completed_this_week = Task.objects.filter(
            status="completed",  # Изменил 'done' на 'completed'
            updated_at__gte=week_ago,
        ).count()

        total_tasks = Task.objects.count()
        active_tasks = Task.objects.exclude(status="completed").count()

        telegram_chat_ids = getattr(settings, "TELEGRAM_CHAT_IDS", {})

        if "admin" in telegram_chat_ids:
            report = f"""📊 <b>ЕЖЕНЕДЕЛЬНЫЙ ОТЧЕТ</b>

📈 За неделю:
   🆕 Создано задач: {created_this_week}
   ✅ Выполнено задач: {completed_this_week}

📋 Общая статистика:
   📌 Всего задач: {total_tasks}
   ⚡ Активных задач: {active_tasks}
   ✅ Выполнено: {total_tasks - active_tasks}

📅 Отчет сформирован: {timezone.now().strftime('%d.%m.%Y %H:%M')}"""

            send_telegram_message(telegram_chat_ids["admin"], report)
            self.stdout.write(self.style.SUCCESS("✅ Еженедельный отчет отправлен"))
