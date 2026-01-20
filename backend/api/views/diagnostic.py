from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from apps.tasks.signals import send_telegram_message


@csrf_exempt
def test_notification(request):
    """Тестовая отправка уведомлений"""
    if request.method == "POST":
        telegram_chat_ids = getattr(settings, "TELEGRAM_CHAT_IDS", {})

        results = {}
        for name, chat_id in telegram_chat_ids.items():
            success = send_telegram_message(
                chat_id,
                f"""🔔 <b>Тестовое уведомление</b>

Система Task Tracker
Получатель: {name}
Время: {timezone.now().strftime('%d.%m.%Y %H:%M:%S')}
Бот: @MyTaskPilotBot

✅ Тестовое сообщение успешно доставлено!""",
            )
            results[name] = "✅ Успешно" if success else "❌ Ошибка"

        return JsonResponse(
            {
                "status": "ok",
                "message": "Тестовые уведомления отправлены",
                "results": results,
            }
        )

    return JsonResponse({"error": "Только POST"}, status=400)


def diagnostic_view(request):
    """Диагностика проблем с проектом"""

    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    data = {
        "status": "Django работает",
        "debug": settings.DEBUG,
        "base_dir": str(BASE_DIR),
        "templates_dirs": [],
        "static_dirs": [],
        "installed_apps": settings.INSTALLED_APPS,
        "template_files_exist": {},
        "static_files_exist": {},
    }

    # Проверяем пути к шаблонам
    for template_dir in settings.TEMPLATES[0]["DIRS"]:
        data["templates_dirs"].append(str(template_dir))
        template_path = Path(template_dir)
        data["template_files_exist"][str(template_dir)] = {
            "dir_exists": template_path.exists(),
            "index.html": (template_path / "index.html").exists(),
            "base.html": (template_path / "base.html").exists(),
        }

    # Проверяем статические файлы
    data["static_dirs"] = str(settings.STATICFILES_DIRS)

    return JsonResponse(data)
