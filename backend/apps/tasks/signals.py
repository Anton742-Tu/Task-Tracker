import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Task
from .telegram_utils import send_telegram_message, get_user_chat_id
from apps.users.models import User

logger = logging.getLogger(__name__)

# Глобальный словарь для хранения предыдущих состояний задач
_task_cache = {}


@receiver(pre_save, sender=Task)
def save_task_state(sender, instance, **kwargs):
    """
    Сохраняем состояние задачи перед сохранением
    """
    if instance.pk:
        try:
            old_instance = Task.objects.get(pk=instance.pk)
            # Сохраняем ВСЕ важные поля
            _task_cache[instance.pk] = {
                "status": old_instance.status,
                "assignee_id": (
                    old_instance.assignee_id if old_instance.assignee else None
                ),
                "due_date": old_instance.due_date,
                "priority": old_instance.priority,
                "title": old_instance.title,
                "description": old_instance.description,
            }
        except Task.DoesNotExist:
            _task_cache[instance.pk] = None
    else:
        _task_cache.get(instance.pk, None)


@receiver(post_save, sender=Task)
def task_notification_system(sender, instance, created, **kwargs):
    """
    Полная система уведомлений для задач
    """
    logger.info(
        f"🔔 [NOTIFICATION] Обработка задачи: '{instance.title}' (ID: {instance.id})"
    )

    old_data = _task_cache.get(instance.pk) if not created else None

    # Определяем, какие поля изменились
    changed_fields = []
    if old_data:
        if old_data.get("status") != instance.status:
            changed_fields.append("status")
        if old_data.get("assignee_id") != (
            instance.assignee_id if instance.assignee else None
        ):
            changed_fields.append("assignee")
        if old_data.get("due_date") != instance.due_date:
            changed_fields.append("due_date")
        if old_data.get("priority") != instance.priority:
            changed_fields.append("priority")
        if old_data.get("title") != instance.title:
            changed_fields.append("title")
        if old_data.get("description") != instance.description:
            changed_fields.append("description")

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
    elif "status" in changed_fields and instance.assignee and instance.assignee.email:
        send_task_email(
            instance,
            recipient=instance.assignee,
            email_type="status_changed",
            project_name=project_name,
            old_status=old_data.get("status") if old_data else None,
        )

    # C. Email исполнителю при изменении сроков
    elif "due_date" in changed_fields and instance.assignee and instance.assignee.email:
        send_task_email(
            instance,
            recipient=instance.assignee,
            email_type="due_date_changed",
            project_name=project_name,
            old_due_date=old_data.get("due_date") if old_data else None,
        )

    # ==========================
    # 2. TELEGRAM УВЕДОМЛЕНИЯ
    # ==========================

    # Уведомление исполнителю
    if instance.assignee:
        chat_id = get_user_chat_id(instance.assignee)

        if chat_id:
            # A. При создании задачи
            if created:
                message = f"""🚀 <b>Вам назначена новая задача!</b>

📌 <b>Задача:</b> {instance.title}
📁 <b>Проект:</b> {project_name}
📅 <b>Срок:</b> {instance.due_date.strftime('%d.%m.%Y') if instance.due_date else 'Не указан'}
🏷️ <b>Приоритет:</b> {instance.get_priority_display()}
📊 <b>Статус:</b> {instance.get_status_display()}"""

                send_telegram_message(chat_id, message)
                logger.info(
                    f"✅ [TELEGRAM] Уведомление о новой задаче отправлено: {instance.assignee.username}"
                )

            # B. При изменении статуса
            elif "status" in changed_fields:
                old_status_display = (
                    old_data.get("status", "неизвестно").replace("_", " ").title()
                )
                new_status_display = instance.status.replace("_", " ").title()

                message = f"""📊 <b>Изменен статус задачи</b>

📌 <b>Задача:</b> {instance.title}
🔄 <b>Статус:</b> {old_status_display} → {new_status_display}
👤 <b>Изменил:</b> {instance.creator.username if instance.creator else 'Система'}"""

                send_telegram_message(chat_id, message)
                logger.info(
                    f"✅ [TELEGRAM] Уведомление о смене статуса отправлено: {instance.assignee.username}"
                )

            # C. При изменении сроков
            elif "due_date" in changed_fields:
                old_date = old_data.get("due_date")
                new_date = instance.due_date

                if old_date and new_date:
                    message = f"""📅 <b>Изменен срок выполнения</b>

📌 <b>Задача:</b> {instance.title}
🔄 <b>Срок:</b> {old_date.strftime('%d.%m.%Y')} → {new_date.strftime('%d.%m.%Y')}"""

                    send_telegram_message(chat_id, message)
                    logger.info(
                        f"✅ [TELEGRAM] Уведомление об изменении срока отправлено: {instance.assignee.username}"
                    )

    # Уведомление админу при ВСЕХ изменениях (если не админ менял)
    admin_chat_id = getattr(settings, "TELEGRAM_CHAT_IDS", {}).get("admin")

    if admin_chat_id and changed_fields and not created:
        # Формируем список изменений
        changes_list = []
        if "status" in changed_fields:
            changes_list.append(
                f"статус: {old_data.get('status', 'неизвестно')} → {instance.status}"
            )
        if "assignee" in changed_fields:
            old_assignee = (
                User.objects.filter(id=old_data.get("assignee_id")).first()
                if old_data.get("assignee_id")
                else None
            )
            changes_list.append(
                f"исполнитель: {old_assignee.username if old_assignee else 'нет'} → {instance.assignee.username if instance.assignee else 'нет'}"
            )
        if "due_date" in changed_fields:
            old_date = old_data.get("due_date")
            new_date = instance.due_date
            changes_list.append(
                f"срок: {old_date.strftime('%d.%m.%Y') if old_date else 'нет'} → {new_date.strftime('%d.%m.%Y') if new_date else 'нет'}"
            )

        if changes_list:
            changes_text = "\n".join([f"• {change}" for change in changes_list])

            message = f"""👁‍🗨 <b>Админ: Задача изменена</b>

📌 <b>Задача:</b> {instance.title} (ID: {instance.id})
👤 <b>Изменил:</b> {instance.creator.username if instance.creator else 'Неизвестно'}

<b>Изменения:</b>
{changes_text}"""

            send_telegram_message(admin_chat_id, message)
            logger.info(
                "✅ [TELEGRAM] Уведомление об изменениях отправлено администратору"
            )

    # Очищаем кэш
    if instance.pk in _task_cache:
        del _task_cache[instance.pk]


def send_task_email(
    task, recipient, email_type, project_name, old_status=None, old_due_date=None
):
    """
    Отправка email уведомления
    """
    try:
        recipient_name = (
            recipient.get_full_name() or recipient.first_name or recipient.username
        )

        if not recipient.email:
            logger.warning(f"⚠️ [EMAIL] У пользователя {recipient.username} нет email")
            return

        if email_type == "new_task":
            subject = f"🚀 Новая задача: {task.title}"

            message = f"""Здравствуйте, {recipient_name}!

Вам назначена новая задача:

📌 Задача: {task.title}
📁 Проект: {project_name}
🏷️ Приоритет: {task.get_priority_display()}
📅 Срок: {task.due_date.strftime('%d.%m.%Y') if task.due_date else 'Не указан'}
📊 Статус: {task.get_status_display()}

Описание:
{task.description if task.description else 'Описание отсутствует'}

Ссылка на задачу: {getattr(settings, 'SITE_URL', 'http://localhost:8000')}/tasks/{task.id}/
"""

        elif email_type == "status_changed":
            subject = f"📝 Изменен статус задачи: {task.title}"

            message = f"""Здравствуйте, {recipient_name}!

Изменен статус задачи:

📌 Задача: {task.title}
🔄 Статус: {old_status} → {task.status}
📁 Проект: {project_name}

Ссылка на задачу: {getattr(settings, 'SITE_URL', 'http://localhost:8000')}/tasks/{task.id}/
"""

        elif email_type == "due_date_changed":
            subject = f"📅 Изменен срок задачи: {task.title}"

            old_date_str = (
                old_due_date.strftime("%d.%m.%Y") if old_due_date else "Не указан"
            )
            new_date_str = (
                task.due_date.strftime("%d.%m.%Y") if task.due_date else "Не указан"
            )

            message = f"""Здравствуйте, {recipient_name}!

Изменен срок выполнения задачи:

📌 Задача: {task.title}
🔄 Срок: {old_date_str} → {new_date_str}
📁 Проект: {project_name}
📊 Статус: {task.get_status_display()}

Ссылка на задачу: {getattr(settings, 'SITE_URL', 'http://localhost:8000')}/tasks/{task.id}/
"""

        else:
            return

        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@tasktracker.ru")

        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[recipient.email],
            fail_silently=False,
        )

        logger.info(f"✅ [EMAIL] Отправлен {email_type} на: {recipient.email}")

    except Exception as e:
        logger.error(
            f"❌ [EMAIL] Ошибка отправки пользователю {recipient.username}: {e}"
        )


# Обновим старую функцию, чтобы она использовала новую
def send_telegram_notification(
    chat_id, task, notification_type, project_name, old_status=None
):
    """
    Отправка уведомления в Telegram о задаче
    (Совместимость со старым кодом)
    """
    try:
        # Формируем текст сообщения
        if notification_type == "new_task_creator":
            text = f"""🚀 <b>Вы создали новую задачу</b>

📌 {task.title}
👤 Исполнитель: {task.assignee.get_full_name() if task.assignee else 'Не назначен'}
📁 Проект: {project_name}
📅 Срок: {task.due_date.strftime('%d.%m.%Y') if task.due_date else 'Не указан'}"""

        elif notification_type == "new_task_assignee":
            text = f"""🚀 <b>Вам назначена новая задача</b>

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
            old_status_display = (
                old_status.replace("_", " ").title() if old_status else ""
            )
            new_status_display = task.status.replace("_", " ").title()
            text = f"""{emoji} <b>Изменен статус задачи</b>

📌 {task.title}
🔄 {old_status_display} → {new_status_display}
👤 Исполнитель: {task.assignee.get_full_name() if task.assignee else 'Не назначен'}"""

        else:
            return False

        return send_telegram_message(chat_id, text)

    except Exception as e:
        print(f"❌ [TELEGRAM] Ошибка формирования сообщения: {e}")
        return False


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
