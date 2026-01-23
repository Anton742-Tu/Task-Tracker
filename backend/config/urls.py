# mypy: ignore-errors
from pathlib import Path

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse, JsonResponse
from django.urls import include, path
from django.shortcuts import redirect, render
from django.contrib.auth import views as auth_views
from apps.users.views import employee_dashboard, employee_profile, custom_logout

# type: ignore - библиотеки без stub-файлов
from drf_yasg import openapi  # type: ignore
from drf_yasg.views import get_schema_view  # type: ignore
from rest_framework import permissions
from api.views import diagnostic, telegram


def home_view(request):
    """Главная страница для неавторизованных пользователей"""
    try:
        import sys
        import django
        from django.db import connection
        from django.utils import timezone

        context = {
            "django_version": django.get_version(),
            "python_version": sys.version.split()[0],
            "database_info": connection.vendor,
            "debug_mode": settings.DEBUG,
            "server_time": timezone.now(),
            "projects_count": 0,
            "total_tasks": 0,
            "todo_count": 0,
            "in_progress_count": 0,
            "review_count": 0,
            "completed_tasks_count": 0,
            "active_tasks_count": 0,
            "users_count": 0,
        }

        # Пробуем получить данные из БД
        try:
            from apps.projects.models import Project
            from apps.tasks.models import Task
            from django.contrib.auth import get_user_model

            context["projects_count"] = Project.objects.count()
            context["total_tasks"] = Task.objects.count()
            context["users_count"] = get_user_model().objects.count()

            # Статистика по статусам
            status_counts = {}
            for task in Task.objects.all():
                status = task.status
                status_counts[status] = status_counts.get(status, 0) + 1

            context.update(
                {
                    "todo_count": status_counts.get("todo", 0),
                    "in_progress_count": status_counts.get("in_progress", 0),
                    "review_count": status_counts.get("review", 0),
                    "completed_tasks_count": status_counts.get("done", 0),
                    "active_tasks_count": (
                        status_counts.get("todo", 0)
                        + status_counts.get("in_progress", 0)
                        + status_counts.get("review", 0)
                    ),
                }
            )

        except Exception as db_error:
            # Если таблицы еще не созданы
            print(f"БД не готова: {db_error}")

        return render(request, "index.html", context)

    except Exception as e:
        # Простой fallback
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Task Tracker</title></head>
        <body>
            <h1>Task Tracker System</h1>
            <p><a href="/admin/login/">Admin Login</a></p>
            <p><a href="/employee/login/">Employee Login</a></p>
            <p>Error: {str(e)}</p>
        </body>
        </html>
        """
        return HttpResponse(html)


def smart_home_redirect(request):
    """Умный редирект на главной странице"""
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_staff:
            return redirect("/admin/")
        else:
            return redirect("/dashboard/")
    else:
        return home_view(request)


def diagnostic_view(request):
    """Диагностическая страница"""
    BASE_DIR = Path(__file__).resolve().parent.parent
    templates_dir = BASE_DIR / "templates"

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

    data = {
        "status": "Django работает!",
        "base_dir": str(BASE_DIR),
        "templates": {
            "dir": str(templates_dir),
            "exists": templates_dir.exists(),
            "files": template_files,
        },
    }
    return JsonResponse(data)


def health_check(request):
    return HttpResponse("OK")


# Swagger/OpenAPI
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

# URL patterns
urlpatterns = [
    # Главная страница
    path("", smart_home_redirect, name="home"),
    # Входы
    path(
        "admin/login/",
        auth_views.LoginView.as_view(
            template_name="admin/login.html",
            redirect_authenticated_user=True,
            next_page="/admin/",
        ),
        name="admin_login",
    ),
    path(
        "employee/login/",
        auth_views.LoginView.as_view(
            template_name="registration/employee_login.html",
            redirect_authenticated_user=True,
            next_page="/dashboard/",
        ),
        name="employee_login",
    ),
    # Выходы
    path(
        "logout/",
        auth_views.LogoutView.as_view(
            template_name="registration/logged_out.html",
            next_page=None,
        ),
        name="logout",
    ),
    path("logout/alt/", custom_logout, name="custom_logout"),
    # Сотрудники
    path("dashboard/", employee_dashboard, name="employee_dashboard"),
    path("profile/", employee_profile, name="employee_profile"),
    # Телеграм
    path("api/telegram-webhook/", telegram.telegram_webhook, name="telegram_webhook"),
    path("api/telegram-info/", telegram.get_bot_info, name="telegram_info"),
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

# Debug toolbar
if settings.DEBUG:
    try:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass

# Media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
