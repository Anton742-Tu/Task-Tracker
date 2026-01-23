import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from typing import Optional

try:
    from apps.tasks.telegram_utils import send_telegram_message

    HAS_TELEGRAM_FUNCTION = True
except ImportError:
    send_telegram_message = None  # type: ignore
    HAS_TELEGRAM_FUNCTION = False


@csrf_exempt
@require_POST
def telegram_webhook(request):
    """
    Обработчик входящих сообщений от Telegram
    """
    try:
        data = json.loads(request.body.decode("utf-8"))

        print(
            f"📨 [TELEGRAM WEBHOOK] Получены данные: {json.dumps(data, indent=2, ensure_ascii=False)}"
        )

        # Обработка сообщений
        if "message" in data:
            message_data = data["message"]
            chat_id = message_data["chat"]["id"]
            text = message_data.get("text", "").strip()
            user_name = message_data["chat"].get("first_name", "Пользователь")

            print(f"👤 Получено от {user_name} (chat_id: {chat_id}): {text}")

            # Обработка команд
            if text.startswith("/"):
                if text == "/start":
                    response_text = f"""👋 Привет, {user_name}!

Я - бот Task Tracker (@MyTaskPilotBot).
Я буду отправлять уведомления о задачах.

Доступные команды:
/help - помощь
/status - статус системы
/test - тестовое сообщение"""

                elif text == "/help":
                    response_text = """ℹ️ <b>Помощь по командам</b>

/start - начать работу с ботом
/help - эта справка
/status - статус системы Task Tracker
/test - отправить тестовое сообщение

📋 <b>Что я умею:</b>
• Отправлять уведомления о новых задачах
• Сообщать об изменении статусов задач
• Отправлять отчеты о просроченных задачах
• Еженедельная статистика"""

                elif text == "/status":
                    response_text = """✅ <b>Статус системы</b>

Системa Task Tracker работает нормально.
Бот @MyTaskPilotBot активен и готов к работе.

Для получения уведомлений:
1. Укажите ваш chat_id в настройках системы
2. Создавайте задачи в админ-панели
3. Получайте уведомления в этом чате"""

                elif text == "/test":
                    response_text = f"""✅ <b>Тестовое сообщение</b>

Привет, {user_name}!
Это тестовое сообщение от бота @MyTaskPilotBot.

Ваш chat_id: <code>{chat_id}</code>
Сохраните его для настройки уведомлений в системе."""

                else:
                    response_text = f"""❓ Неизвестная команда: {text}

Используйте /help для списка доступных команд."""

                # Отправляем ответ пользователю
                if HAS_TELEGRAM_FUNCTION and send_telegram_message is not None:
                    send_telegram_message(chat_id, response_text)
                else:
                    print("⚠️ Функция send_telegram_message не найдена")

                # Логируем для админа
                telegram_chat_ids = getattr(settings, "TELEGRAM_CHAT_IDS", {})
                admin_chat_id = telegram_chat_ids.get("admin")
                if (
                    admin_chat_id
                    and HAS_TELEGRAM_FUNCTION
                    and send_telegram_message is not None
                ):
                    admin_message = f"""📨 Новое взаимодействие с ботом:

👤 Пользователь: {user_name}
🆔 Chat ID: {chat_id}
💬 Команда: {text}
⏰ Время: {message_data.get('date', 'не указано')}"""

                    send_telegram_message(admin_chat_id, admin_message)

        return JsonResponse({"ok": True})

    except json.JSONDecodeError as e:
        print(f"❌ [TELEGRAM WEBHOOK] Ошибка парсинга JSON: {e}")
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)
    except Exception as e:
        print(f"❌ [TELEGRAM WEBHOOK] Неожиданная ошибка: {e}")
        return JsonResponse({"ok": False, "error": str(e)}, status=500)


@csrf_exempt
def get_bot_info(request):
    """
    Получение информации о боте (для диагностики)
    """
    try:
        import requests
        from django.conf import settings

        bot_token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)

        if not bot_token:
            return JsonResponse({"error": "Токен бота не настроен"}, status=400)

        # Получаем информацию о боте
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        bot_info = response.json()

        # Получаем информацию о вебхуке
        webhook_url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        webhook_response = requests.get(webhook_url, timeout=10)
        webhook_info = webhook_response.json()

        return JsonResponse(
            {
                "bot": bot_info,
                "webhook": webhook_info,
                "settings": {
                    "bot_token_configured": bool(bot_token),
                    "chat_ids": getattr(settings, "TELEGRAM_CHAT_IDS", {}),
                    "site_url": getattr(settings, "SITE_URL", "Not set"),
                },
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
