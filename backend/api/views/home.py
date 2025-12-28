import django
from django.db import connection
from django.shortcuts import render
from django.utils import timezone

from apps.projects.models import Project
from apps.tasks.models import Task


def home_view(request):
    """Главная страница с информацией о системе"""

    # Получаем статистику
    projects_count = Project.objects.count()
    active_tasks_count = Task.objects.filter(status="in_progress").count()
    completed_tasks_count = Task.objects.filter(status="completed").count()

    # Получаем последние проекты
    projects = Project.objects.all()[:10]  # Ограничиваем 10 проектами

    # Информация о системе
    context = {
        "projects_count": projects_count,
        "active_tasks_count": active_tasks_count,
        "completed_tasks_count": completed_tasks_count,
        "projects": projects,
        "django_version": django.get_version(),
        "database_info": connection.vendor,
        "debug_mode": django.conf.settings.DEBUG,
        "server_time": timezone.now(),
    }

    return render(request, "index.html", context)
