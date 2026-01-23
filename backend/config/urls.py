# mypy: ignore-errors
from pathlib import Path

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse, JsonResponse
from django.urls import include, path

# type: ignore - библиотеки без stub-файлов
from drf_yasg import openapi  # type: ignore
from drf_yasg.views import get_schema_view  # type: ignore
from rest_framework import permissions
from api.views import diagnostic, telegram
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from apps.users.views import employee_dashboard, employee_profile


def home_view(request):
    """Главная страница - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
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

        # Пробуем получить данные из БД
        try:
            # Проекты
            from apps.projects.models import Project

            context["projects_count"] = Project.objects.count()

            # Задачи - ПРАВИЛЬНЫЙ ПОДСЧЕТ!
            from apps.tasks.models import Task

            # Подсчет ВРУЧНУЮ
            status_counts = {}
            for task in Task.objects.all():
                status = task.status  # 'todo', 'in_progress', 'review', 'done'
                status_counts[status] = status_counts.get(status, 0) + 1

            # Заполняем контекст
            context["total_tasks"] = Task.objects.count()
            context["todo_count"] = status_counts.get("todo", 0)
            context["in_progress_count"] = status_counts.get("in_progress", 0)
            context["review_count"] = status_counts.get("review", 0)
            context["completed_tasks_count"] = status_counts.get(
                "done", 0
            )  # 'done', не 'completed'!

            # Активные задачи = все кроме 'done'
            context["active_tasks_count"] = (
                status_counts.get("todo", 0)
                + status_counts.get("in_progress", 0)
                + status_counts.get("review", 0)
            )

            # Пользователи
            from django.contrib.auth import get_user_model

            User = get_user_model()
            context["users_count"] = User.objects.count()

            # Для отладки
            context["status_counts"] = status_counts
            context["debug_message"] = f"✅ Данные из БД: {status_counts}"

        except Exception as db_error:
            # Если таблицы еще не созданы
            print(f"БД не готова: {db_error}")
            context.update(
                {
                    "projects_count": 0,
                    "total_tasks": 0,
                    "active_tasks_count": 0,
                    "completed_tasks_count": 0,
                    "users_count": 0,
                    "todo_count": 0,
                    "in_progress_count": 0,
                    "review_count": 0,
                    "debug_message": "❌ Ошибка БД",
                }
            )

        return render(request, "index.html", context)

    except Exception as e:
        # Если что-то пошло не так
        import traceback

        error_details = f"{str(e)}\n\n{traceback.format_exc()}"
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Ошибка</title><style>body{{font-family:Arial;padding:20px;}}</style></head>
        <body>
            <h1>Ошибка в шаблоне</h1>
            <pre style="background:#f0f0f0;padding:10px;border-radius:5px;">{error_details}</pre>
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
    authentication_classes=[],
)

# 3. Основные URL patterns
urlpatterns = [
    # Отдельный вход для сотрудников
    path(
        "login/employee/",
        auth_views.LoginView.as_view(
            template_name="registration/employee_login.html",
            redirect_authenticated_user=True,
            next_page="/dashboard/",
        ),
        name="employee_login",
    ),
    # ОСТАВЬТЕ ТОЛЬКО ОДИН из этих путей:
    # Либо этот:
    path("", RedirectView.as_view(pattern_name="employee_dashboard")),
    # Либо этот:
    # path("", home_view, name="home"),
    # Уберите дублирование include:
    # path("users/", include("apps.users.urls")),  # если нужно /users/dashboard/
    # path("", include("apps.users.urls")),  # если нужно /dashboard/
    # Телеграм webhook
    path("api/telegram-webhook/", telegram.telegram_webhook, name="telegram_webhook"),
    path("api/telegram-info/", telegram.get_bot_info, name="telegram_info"),
    # Для сотрудников (если не используете include)
    path("dashboard/", employee_dashboard, name="employee_dashboard"),
    path("profile/", employee_profile, name="employee_profile"),
    # Диагностика
    path(
        "api/test-notification/", diagnostic.test_notification, name="test_notification"
    ),
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

# 4. Debug toolbar - только для разработки
if settings.DEBUG:
    try:
        import debug_toolbar  # type: ignore

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass

# Только для development режима
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
