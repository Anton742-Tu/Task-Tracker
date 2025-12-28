from pathlib import Path

from django.conf import settings
from django.http import JsonResponse


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
