import django
import sys
from django.db import connection
from django.db.models import Count, Q
from django.shortcuts import render
from django.utils import timezone

from apps.projects.models import Project
from apps.tasks.models import Task
from apps.users.models import User


def home_view(request):
    """Главная страница с информацией о системе"""

    # Получаем статистику
    projects_count = Project.objects.count()

    # Считаем задачи по статусам - берем реальные значения из базы
    tasks_by_status = Task.objects.values("status").annotate(count=Count("id"))

    print("🔍 DEBUG: Статусы задач из базы:")
    for item in tasks_by_status:
        print(f"  {item['status']}: {item['count']}")

    # Преобразуем в словарь
    status_counts = {item["status"]: item["count"] for item in tasks_by_status}

    # Проверим какие статусы есть
    print(f"🔍 DEBUG: Словарь статусов: {status_counts}")

    # Активные задачи = все кроме 'completed' и 'cancelled'
    # Но статусы могут быть на русском!
    active_tasks_count = Task.objects.exclude(
        Q(status="completed")
        | Q(status="cancelled")
        | Q(status="завершено")
        | Q(status="отменено")
    ).count()

    print(f"🔍 DEBUG: Активных задач: {active_tasks_count}")

    # Получаем конкретные счетчики
    todo_count = status_counts.get("todo", 0) + status_counts.get("К выполнению", 0)
    in_progress_count = status_counts.get("in_progress", 0) + status_counts.get(
        "В процессе", 0
    )
    review_count = status_counts.get("review", 0) + status_counts.get("На проверке", 0)
    completed_count = status_counts.get("completed", 0) + status_counts.get(
        "Завершено", 0
    )

    users_count = User.objects.count()

    # Получаем проекты
    projects = Project.objects.annotate(task_count=Count("tasks")).order_by(
        "-created_at"
    )[:5]

    context = {
        "show_demo": False,
        "projects_count": projects_count,
        "active_tasks_count": active_tasks_count,
        "completed_tasks_count": completed_count,
        "users_count": users_count,
        "todo_count": todo_count,
        "in_progress_count": in_progress_count,
        "review_count": review_count,
        "projects": projects,
        "django_version": django.get_version(),
        "python_version": sys.version.split()[0],
        "database_info": connection.vendor,
        "debug_mode": django.conf.settings.DEBUG,
        "server_time": timezone.now(),
    }

    print(f"🔍 DEBUG: Контекст: {context}")

    return render(request, "index.html", context)
