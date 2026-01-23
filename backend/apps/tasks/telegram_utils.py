import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_telegram_message(chat_id, message, parse_mode="HTML"):
    """
    Универсальная функция отправки сообщений в Telegram
    """
    TELEGRAM_BOT_TOKEN = getattr(settings, "TELEGRAM_BOT_TOKEN", None)

    if not TELEGRAM_BOT_TOKEN:
        logger.warning("⚠️ [TELEGRAM] Токен бота не настроен")
        return False

    if not chat_id:
        logger.warning("⚠️ [TELEGRAM] Не указан chat_id для отправки сообщения")
        return False

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": parse_mode}

        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()

        logger.info(f"✅ [TELEGRAM] Сообщение отправлено в чат {chat_id}")
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ [TELEGRAM] Ошибка отправки: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ [TELEGRAM] Неожиданная ошибка: {e}")
        return False


def get_user_chat_id(user):
    """
    Получение chat_id пользователя в порядке приоритета:
    1. Из поля telegram_chat_id в модели User (если есть)
    2. Из TELEGRAM_CHAT_IDS по user.id
    3. Из TELEGRAM_CHAT_IDS по username
    """
    TELEGRAM_CHAT_IDS = getattr(settings, "TELEGRAM_CHAT_IDS", {})

    if not user:
        return None

    # 1. ПРОВЕРЯЕМ ПОЛЕ В МОДЕЛИ (самый надежный способ)
    if hasattr(user, "telegram_chat_id") and user.telegram_chat_id:
        chat_id = user.telegram_chat_id
        if is_valid_chat_id(chat_id):
            return chat_id

    # 2. ИЩЕМ ПО ID пользователя
    if hasattr(user, "id"):
        chat_id = TELEGRAM_CHAT_IDS.get(str(user.id))
        if is_valid_chat_id(chat_id):
            return chat_id

    # 3. ИЩЕМ ПО username (менее надежно)
    if hasattr(user, "username"):
        chat_id = TELEGRAM_CHAT_IDS.get(user.username)
        if is_valid_chat_id(chat_id):
            return chat_id

    # 4. НЕ ИЩЕМ ПО EMAIL! (разные системы)

    return None


def is_valid_chat_id(chat_id):
    """Проверка валидности chat_id"""
    if not chat_id:
        return False

    # Убираем пробелы
    chat_id = str(chat_id).strip()

    # Пустая строка
    if not chat_id:
        return False

    # Проверяем, что это число
    try:
        chat_id_int = int(chat_id)
        # Telegram chat_id всегда положительный
        return chat_id_int > 0
    except ValueError:
        return False
