import requests
from django.conf import settings
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def send_telegram_message(chat_id: str, message: str, parse_mode: str = "HTML") -> bool:
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


def get_user_chat_id(user) -> Optional[str]:
    """
    Получение chat_id пользователя в порядке приоритета:
    1. Из поля telegram_chat_id в модели User (самый надежный способ)
    2. Из TELEGRAM_CHAT_IDS по user.id
    3. Из TELEGRAM_CHAT_IDS по username
    4. Из отдельной модели telegram_settings (если используется)
    """
    TELEGRAM_CHAT_IDS = getattr(settings, "TELEGRAM_CHAT_IDS", {})

    if not user:
        return None

    # 1. ПРОВЕРЯЕМ ПОЛЕ В МОДЕЛИ USER (самый надежный способ)
    if hasattr(user, "telegram_chat_id") and user.telegram_chat_id:
        chat_id = user.telegram_chat_id
        if is_valid_chat_id(chat_id):
            logger.debug(f"✅ Найден chat_id в поле модели: {chat_id}")
            return chat_id

    # 2. ИЗ ОТДЕЛЬНОЙ МОДЕЛИ TELEGRAM_SETTINGS (если используете)
    if hasattr(user, "telegram_settings"):
        if user.telegram_settings and hasattr(user.telegram_settings, "chat_id"):
            chat_id = user.telegram_settings.chat_id
            if chat_id and is_valid_chat_id(chat_id):
                logger.debug(f"✅ Найден chat_id в telegram_settings: {chat_id}")
                return chat_id

    # 3. ИЩЕМ ПО ID пользователя в TELEGRAM_CHAT_IDS
    if hasattr(user, "id"):
        chat_id = TELEGRAM_CHAT_IDS.get(str(user.id))
        if is_valid_chat_id(chat_id):
            logger.debug(f"✅ Найден chat_id по user.id {user.id}: {chat_id}")
            return chat_id

    # 4. ИЩЕМ ПО username в TELEGRAM_CHAT_IDS (менее надежно)
    if hasattr(user, "username"):
        chat_id = TELEGRAM_CHAT_IDS.get(user.username)
        if is_valid_chat_id(chat_id):
            logger.debug(f"✅ Найден chat_id по username {user.username}: {chat_id}")
            return chat_id

    # 5. ИЩЕМ ПО email (только если очень нужно)
    # НЕ РЕКОМЕНДУЕТСЯ: email и telegram - разные системы!
    # if hasattr(user, "email"):
    #     chat_id = TELEGRAM_CHAT_IDS.get(user.email)
    #     if is_valid_chat_id(chat_id):
    #         return chat_id

    logger.warning(
        f"⚠️ Не найден chat_id для пользователя {user.username} (ID: {user.id})"
    )
    return None


def is_valid_chat_id(chat_id) -> bool:
    """
    Проверка валидности chat_id
    """
    if not chat_id:
        return False

    # Убираем пробелы и преобразуем в строку
    chat_id_str = str(chat_id).strip()

    # Пустая строка
    if not chat_id_str:
        return False

    # Проверяем, что это число (Telegram chat_id всегда числовой)
    try:
        chat_id_int = int(chat_id_str)
        # Telegram chat_id всегда положительный
        if chat_id_int > 0:
            return True
        else:
            logger.warning(f"⚠️ Отрицательный chat_id: {chat_id_str}")
            return False
    except ValueError:
        # Может быть строковым для приватных каналов (начинается с @)
        if chat_id_str.startswith("@") and len(chat_id_str) > 1:
            return True
        elif chat_id_str.startswith("-100"):  # ID каналов/групп
            try:
                int(chat_id_str)
                return True
            except ValueError:
                return False
        logger.warning(f"⚠️ Невалидный формат chat_id: {chat_id_str}")
        return False


def test_telegram_connection() -> dict:
    """
    Тест соединения с Telegram API
    """
    TELEGRAM_BOT_TOKEN = getattr(settings, "TELEGRAM_BOT_TOKEN", None)

    if not TELEGRAM_BOT_TOKEN:
        return {"success": False, "error": "Токен бота не настроен"}

    try:
        # Тест получения информации о боте
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        bot_info = response.json()

        # Тест отправки (если есть тестовый chat_id)
        TELEGRAM_CHAT_IDS = getattr(settings, "TELEGRAM_CHAT_IDS", {})
        test_chat_id = TELEGRAM_CHAT_IDS.get("admin") or TELEGRAM_CHAT_IDS.get("test")

        send_test = False
        if test_chat_id and is_valid_chat_id(test_chat_id):
            test_message = "✅ Тестовое сообщение от Task Tracker"
            send_test = send_telegram_message(test_chat_id, test_message)

        return {
            "success": True,
            "bot_info": bot_info,
            "test_sent": send_test,
            "test_chat_id": test_chat_id,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def get_user_by_chat_id(chat_id: str):
    """
    Поиск пользователя по chat_id
    Обратная функция для вебхука Telegram
    """
    from apps.users.models import User

    if not chat_id or not is_valid_chat_id(chat_id):
        return None

    # 1. Ищем по полю telegram_chat_id
    try:
        user = User.objects.get(telegram_chat_id=chat_id)
        return user
    except User.DoesNotExist:
        pass
    except User.MultipleObjectsReturned:
        # Нашли несколько пользователей с одинаковым chat_id
        users = User.objects.filter(telegram_chat_id=chat_id)
        return users.first()

    # 2. Ищем в TELEGRAM_CHAT_IDS
    TELEGRAM_CHAT_IDS = getattr(settings, "TELEGRAM_CHAT_IDS", {})

    # Ищем chat_id среди значений
    for key, value in TELEGRAM_CHAT_IDS.items():
        if value == chat_id:
            # key может быть 'admin', '1' (user.id), 'username'
            if key == "admin":
                # Ищем администратора
                return User.objects.filter(is_superuser=True).first()
            elif key.isdigit():
                # Ищем по ID
                try:
                    return User.objects.get(id=int(key))
                except User.DoesNotExist:
                    continue
            else:
                # Ищем по username
                try:
                    return User.objects.get(username=key)
                except User.DoesNotExist:
                    continue

    return None
