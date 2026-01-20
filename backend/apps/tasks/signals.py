import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Task

logger = logging.getLogger(__name__)

# Telegram настройки (вынеси в settings или .env)
TELEGRAM_BOT_TOKEN = (
    settings.TELEGRAM_BOT_TOKEN if hasattr(settings, "TELEGRAM_BOT_TOKEN") else None
)
TELEGRAM_CHAT_IDS = getattr(settings, "TELEGRAM_CHAT_IDS", {})


@receiver(post_save, sender=Task)
def task_notification_system(sender, instance, created, **kwargs):
    """
    Полная система уведомлений для задач:
    1. Email при создании/изменении
    2. Email при изменении статуса
    3. Telegram уведомления
    """
    print(f"\n🔔 [NOTIFICATION] Задача: '{instance.title}' (ID: {instance.id})")

    # Получаем изменения
    if hasattr(instance, "_previous_status"):
        status_changed = instance._previous_status != instance.status
        old_status = instance._previous_status
    else:
        status_changed = False
        old_status = None

    # Получаем название проекта
    project_name = instance.project.name if instance.project else "Без проекта"

    # ====================
    # 1. EMAIL УВЕДОМЛЕНИЯ
    # ====================

    # A. Email исполнителю при создании
    if created and instance.assignee and instance.assignee.email:
        send_task_email(
            instance,
            recipient=instance.assignee,
            email_type="new_task",
            project_name=project_name,
        )

    # B. Email исполнителю при изменении статуса
    elif status_changed and instance.assignee and instance.assignee.email:
        send_task_email(
            instance,
            recipient=instance.assignee,
            email_type="status_changed",
            project_name=project_name,
            old_status=old_status,
        )

    # C. Email создателю при завершении задачи
    elif (
        status_changed
        and instance.status == "completed"
        and instance.creator
        and instance.creator.email
        and instance.creator != instance.assignee
    ):  # Не отправляем если это один человек
        send_task_email(
            instance,
            recipient=instance.creator,
            email_type="task_completed",
            project_name=project_name,
            old_status=old_status,
        )

    # ==========================
    # 2. TELEGRAM УВЕДОМЛЕНИЯ
    # ==========================

    if TELEGRAM_BOT_TOKEN:
        # A. Telegram создателю при создании задачи
        if (
            created
            and instance.creator
            and instance.creator.username in TELEGRAM_CHAT_IDS
        ):
            send_telegram_notification(
                chat_id=TELEGRAM_CHAT_IDS[instance.creator.username],
                task=instance,
                notification_type="new_task_creator",
                project_name=project_name,
            )

        # B. Telegram исполнителю при создании/изменении
        if instance.assignee and instance.assignee.username in TELEGRAM_CHAT_IDS:
            if created:
                send_telegram_notification(
                    chat_id=TELEGRAM_CHAT_IDS[instance.assignee.username],
                    task=instance,
                    notification_type="new_task_assignee",
                    project_name=project_name,
                )
            elif status_changed:
                send_telegram_notification(
                    chat_id=TELEGRAM_CHAT_IDS[instance.assignee.username],
                    task=instance,
                    notification_type="status_changed",
                    project_name=project_name,
                    old_status=old_status,
                )


def send_task_email(task, recipient, email_type, project_name, old_status=None):
    """
    Отправка email уведомления
    """
    try:
        # Имя получателя
        recipient_name = (
            recipient.get_full_name() or recipient.first_name or recipient.username
        )

        # Подготавливаем данные для шаблона
        context = {
            "task": task,
            "recipient": recipient,
            "recipient_name": recipient_name,
            "project_name": project_name,
            "old_status": old_status,
            "site_url": getattr(settings, "SITE_URL", "http://localhost:8000"),
        }

        # Выбираем тему и шаблон
        if email_type == "new_task":
            subject = f"🚀 Новая задача: {task.title}"
            template = "emails/task_created.html"
        elif email_type == "status_changed":
            subject = f"📝 Изменен статус задачи: {task.title}"
            template = "emails/task_status_changed.html"
            context["status_change"] = f"{old_status} → {task.status}"
        elif email_type == "task_completed":
            subject = f"✅ Задача выполнена: {task.title}"
            template = "emails/task_completed.html"
        else:
            return

        # Рендерим HTML и plain text версии
        html_message = render_to_string(template, context)
        plain_message = strip_tags(html_message)

        # Отправляем
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL or "noreply@tasktracker.ru",
            recipient_list=[recipient.email],
            html_message=html_message,
            fail_silently=False,
        )

        print(f"✅ [EMAIL] Отправлен {email_type} на: {recipient.email}")

    except Exception as e:
        print(f"❌ [EMAIL] Ошибка отправки: {e}")


def send_telegram_notification(
    chat_id, task, notification_type, project_name, old_status=None
):
    """
    Отправка уведомления в Telegram
    """
    try:
        import requests

        # Формируем текст сообщения
        if notification_type == "new_task_creator":
            text = f"""🚀 Вы создали новую задачу:

📌 {task.title}
👤 Исполнитель: {task.assignee.get_full_name() if task.assignee else 'Не назначен'}
📁 Проект: {project_name}
📅 Срок: {task.due_date.strftime('%d.%m.%Y') if task.due_date else 'Не указан'}"""

        elif notification_type == "new_task_assignee":
            text = f"""🚀 Вам назначена новая задача:

📌 {task.title}
👤 От: {task.creator.get_full_name() if task.creator else 'Система'}
📁 Проект: {project_name}
📅 Срок: {task.due_date.strftime('%d.%m.%Y') if task.due_date else 'Не указан'}
🏷️ Приоритет: {task.get_priority_display()}"""

        elif notification_type == "status_changed":
            status_emojis = {
                "todo": "📋",
                "in_progress": "⚡",
                "review": "👀",
                "completed": "✅",
            }
            emoji = status_emojis.get(task.status, "📝")
            text = f"""{emoji} Изменен статус задачи:

📌 {task.title}
🔄 {old_status} → {task.status}
👤 Исполнитель: {task.assignee.get_full_name() if task.assignee else 'Не назначен'}"""

        else:
            return

        # URL для отправки
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

        # Отправляем
        response = requests.post(
            url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        )

        if response.status_code == 200:
            print(f"✅ [TELEGRAM] Уведомление отправлено в чат {chat_id}")
        else:
            print(f"⚠️ [TELEGRAM] Ошибка: {response.json()}")

    except ImportError:
        print("⚠️ [TELEGRAM] Библиотека requests не установлена")
    except Exception as e:
        print(f"❌ [TELEGRAM] Ошибка: {e}")


# Сигнал для сохранения предыдущего статуса
@receiver(post_save, sender=Task)
def save_previous_status(sender, instance, **kwargs):
    """
    Сохраняем предыдущий статус задачи для отслеживания изменений
    """
    if instance.pk:
        try:
            old_instance = Task.objects.get(pk=instance.pk)
            instance._previous_status = old_instance.status
        except Task.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None
