from pathlib import Path

from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse, JsonResponse
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


def home_view(request):
    """Главная страница"""
    try:
        import sys

        import django
        from django.db import connection
        from django.shortcuts import render
        from django.utils import timezone

        # Базовый контекст
        context = {
            "django_version": django.get_version(),
            "python_version": sys.version.split()[0],
            "database_info": connection.vendor,
            "debug_mode": django.conf.settings.DEBUG,
            "server_time": timezone.now(),
        }

        # Пробуем получить данные из БД (если таблицы существуют)
        try:
            # Проекты
            from apps.projects.models import Project

            context["projects_count"] = Project.objects.count()

            # Задачи
            from apps.tasks.models import Task

            context["active_tasks_count"] = Task.objects.filter(
                status="in_progress"
            ).count()
            context["completed_tasks_count"] = Task.objects.filter(
                status="completed"
            ).count()

            # Пользователи
            from django.contrib.auth import get_user_model

            User = get_user_model()
            context["users_count"] = User.objects.count()

        except Exception as db_error:
            # Если таблицы еще не созданы
            print(f"БД не готова: {db_error}")
            context["projects_count"] = 0
            context["active_tasks_count"] = 0
            context["completed_tasks_count"] = 0
            context["users_count"] = 0

        return render(request, "index.html", context)

    except Exception as e:
        # Если что-то пошло не так
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Ошибка</title><style>body{{font-family:Arial;padding:20px;}}</style></head>
        <body>
            <h1>Ошибка в шаблоне</h1>
            <pre style="background:#f0f0f0;padding:10px;border-radius:5px;">{str(e)}</pre>
            <p><a href="/">На главную</a></p>
        </body>
        </html>
        """
        return HttpResponse(html)


def diagnostic_view(request):
    BASE_DIR = Path(__file__).resolve().parent.parent
    templates_dir = BASE_DIR / "templates"

    # Проверяем, что внутри templates/
    template_files = []
    if templates_dir.exists():
        for file in templates_dir.iterdir():
            template_files.append(
                {
                    "name": file.name,
                    "size": file.stat().st_size,
                    "is_file": file.is_file(),
                }
            )

    # Получаем настройки TEMPLATES
    templates_settings = {
        "DIRS": [str(d) for d in settings.TEMPLATES[0]["DIRS"]],
        "APP_DIRS": settings.TEMPLATES[0]["APP_DIRS"],
        "BACKEND": settings.TEMPLATES[0]["BACKEND"],
    }

    data = {
        "status": "Django работает!",
        "base_dir": str(BASE_DIR),
        "templates": {
            "dir": str(templates_dir),
            "exists": templates_dir.exists(),
            "files": template_files,
            "settings": templates_settings,
        },
        "static": {
            "dir": str(BASE_DIR / "static"),
            "exists": (BASE_DIR / "static").exists(),
        },
    }
    return JsonResponse(data)


def health_check(request):
    return HttpResponse("OK")


# 2. Swagger/OpenAPI
schema_view = get_schema_view(
    openapi.Info(
        title="Task Tracker API",
        default_version="v1",
        description="API для системы управления задачами",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# 3. Основные URL patterns
urlpatterns = [
    # Главная
    path("", home_view, name="home"),
    # Диагностика
    path("diagnostic/", diagnostic_view, name="diagnostic"),
    # Health check
    path("health/", health_check, name="health"),
    # Админка
    path("admin/", admin.site.urls),
    # API
    path("api/", include("api.urls")),
    # Документация
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

# 4. Debug toolbar
if settings.DEBUG:
    try:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
