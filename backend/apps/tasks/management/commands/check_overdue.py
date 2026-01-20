from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.tasks.models import Task
from apps.tasks.signals import send_telegram_message
from django.conf import settings


class Command(BaseCommand):
    help = "Проверка просроченных задач и отправка уведомлений"

    def handle(self, *args, **options):
        today = timezone.now().date()
        overdue_tasks = Task.objects.filter(
            due_date__lt=today, status__in=["todo", "in_progress"]
        ).exclude(
            status="completed"
        )  # Изменил 'done' на 'completed'

        self.stdout.write(f"🔍 Найдено просроченных задач: {overdue_tasks.count()}")

        telegram_chat_ids = getattr(settings, "TELEGRAM_CHAT_IDS", {})

        for task in overdue_tasks:
            self.stdout.write(f"⚠️  Просрочена: {task.title} (срок: {task.due_date})")

            # Уведомление админу
            if "admin" in telegram_chat_ids:
                message = f"""🚨 <b>ПРОСРОЧЕНА ЗАДАЧА</b>

📌 {task.title}
👤 Исполнитель: {task.assignee.get_full_name() if task.assignee else "Не назначен"}
📅 Срок был: {task.due_date.strftime('%d.%m.%Y')}
⏰ Просрочка: {(today - task.due_date).days} дней
🏷️ Приоритет: {task.get_priority_display()}
📁 Проект: {task.project.name if task.project else "Без проекта"}"""

                send_telegram_message(telegram_chat_ids["admin"], message)

        self.stdout.write(self.style.SUCCESS("✅ Проверка завершена"))
