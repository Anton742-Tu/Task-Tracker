import requests
import json
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class TelegramService:
    """Сервис для отправки уведомлений в Telegram"""

    def __init__(self):
        self.bot_token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
        self.chat_ids = getattr(settings, "TELEGRAM_CHAT_IDS", {})
        self.site_url = getattr(settings, "SITE_URL", "")

    def send_message(
        self, chat_id, message, parse_mode="HTML", disable_notification=False
    ):
        """Отправка сообщения в Telegram"""
        if not self.bot_token or not chat_id:
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": parse_mode,
            "disable_notification": disable_notification,
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Ошибка отправки в Telegram: {e}")
            return False

    def send_to_user(self, username, message, **kwargs):
        """Отправка сообщения конкретному пользователю по username"""
        chat_id = self.chat_ids.get(username)
        if chat_id:
            return self.send_message(chat_id, message, **kwargs)
        return False

    def send_to_admin(self, message, **kwargs):
        """Отправка сообщения администратору"""
        return self.send_to_user("admin", message, **kwargs)

    def send_to_all(self, message, **kwargs):
        """Отправка сообщения всем зарегистрированным пользователям"""
        success_count = 0
        for username, chat_id in self.chat_ids.items():
            if self.send_message(chat_id, message, **kwargs):
                success_count += 1
        return success_count

    def send_task_notification(self, task, action="created"):
        """Отправка уведомления о задаче"""
        action_messages = {
            "created": "создана",
            "updated": "обновлена",
            "assigned": "назначена",
            "completed": "выполнена",
        }

        action_text = action_messages.get(action, "изменена")

        # Формируем сообщение
        message = f"""
<b>📋 Новая задача {action_text}</b>

<b>Задача:</b> {task.title}
<b>Проект:</b> {task.project.name if task.project else 'Без проекта'}
<b>Приоритет:</b> {task.get_priority_display()}
<b>Статус:</b> {task.get_status_display()}
<b>Создатель:</b> {task.creator.get_full_name() or task.creator.username}
"""

        if task.assignee:
            message += f"<b>Исполнитель:</b> {task.assignee.get_full_name() or task.assignee.username}\n"

        if task.due_date:
            message += f"<b>Срок:</b> {task.due_date.strftime('%d.%m.%Y')}\n"

        if self.site_url:
            message += (
                f"\n<a href='{self.site_url}/tasks/{task.id}/'>👀 Посмотреть задачу</a>"
            )

        # Отправляем админу
        self.send_to_admin(message)

        # Отправляем исполнителю, если он есть и у него есть chat_id
        if task.assignee:
            # Предполагаем, что username в Telegram совпадает с username в системе
            telegram_username = task.assignee.username
            if telegram_username in self.chat_ids:
                self.send_to_user(telegram_username, message)

        return True

    def test_connection(self):
        """Тест подключения к боту"""
        if not self.bot_token:
            return False, "Токен бота не настроен"

        url = f"https://api.telegram.org/bot{self.bot_token}/getMe"

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return (
                    True,
                    f"Бот: {data.get('result', {}).get('username', 'Неизвестно')}",
                )
            else:
                return False, f"Ошибка API: {response.status_code}"
        except Exception as e:
            return False, f"Ошибка подключения: {e}"


telegram_service = TelegramService()
