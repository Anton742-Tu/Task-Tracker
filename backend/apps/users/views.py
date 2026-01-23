from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone


@login_required
def employee_dashboard(request):
    """Дашборд для сотрудника"""
    from apps.tasks.models import Task

    # Получаем задачи сотрудника
    tasks = Task.objects.filter(assignee=request.user).order_by("-created_at")

    context = {
        "user": request.user,
        "tasks": tasks,
        "active_tasks": tasks.filter(status__in=["todo", "in_progress"]),
        "completed_tasks": tasks.filter(status="completed"),
        "overdue_tasks": (
            tasks.filter(
                status__in=["todo", "in_progress"], due_date__lt=timezone.now().date()
            )
            if hasattr(tasks, "filter")
            else []
        ),
    }

    return render(request, "users/employee_dashboard.html", context)


@login_required
def employee_profile(request):
    """Профиль сотрудника"""
    if request.method == "POST":
        # Обновление профиля
        user = request.user
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.email = request.POST.get("email", user.email)
        user.telegram_chat_id = request.POST.get(
            "telegram_chat_id", user.telegram_chat_id
        )
        user.save()

        messages.success(request, "Профиль обновлен")
        return redirect("employee_profile")

    return render(request, "users/employee_profile.html", {"user": request.user})
