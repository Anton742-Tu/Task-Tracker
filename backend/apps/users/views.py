from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.contrib.auth import logout as auth_logout
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST


def employee_required(view_func):
    """Декоратор для проверки, что пользователь не админ"""

    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("/employee/login/")

        # Проверяем, что это не суперпользователь (админ)
        if request.user.is_superuser or request.user.is_staff:
            # Админов отправляем в админку
            return redirect("/admin/")

        return view_func(request, *args, **kwargs)

    return wrapper


@employee_required
def employee_dashboard(request):
    """Дашборд для сотрудника"""
    from apps.tasks.models import Task

    user = request.user

    # Получаем задачи сотрудника
    tasks = Task.objects.filter(assignee=user).order_by("-created_at")

    # Правильные фильтры (адаптируйте под ваши статусы)
    active_tasks = tasks.exclude(status="done")
    completed_tasks = tasks.filter(status="done")

    # Просроченные задачи
    overdue_tasks = tasks.filter(
        due_date__lt=timezone.now().date(), status__in=["todo", "in_progress", "review"]
    )

    # Статистика по статусам
    status_stats = {}
    for task in tasks:
        status = task.status
        status_stats[status] = status_stats.get(status, 0) + 1

    context = {
        "user": user,
        "tasks": tasks,
        "active_tasks": active_tasks,
        "completed_tasks": completed_tasks,
        "overdue_tasks": overdue_tasks,
        "status_stats": status_stats,
        "today": timezone.now().date(),
    }

    return render(request, "users/employee_dashboard.html", context)


@employee_required
def employee_profile(request):
    """Профиль сотрудника - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
    if request.method == "POST":
        # Проверяем текущий пароль для безопасности
        current_password = request.POST.get("current_password", "")

        if not request.user.check_password(current_password):
            messages.error(request, "Неверный текущий пароль")
            return redirect("employee_profile")

        # Обновление профиля
        user = request.user

        # Проверяем email на уникальность
        new_email = request.POST.get("email", "")
        if new_email != user.email:
            from apps.users.models import User

            if User.objects.filter(email=new_email).exclude(id=user.id).exists():
                messages.error(request, "Этот email уже используется")
                return redirect("employee_profile")

        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.email = new_email

        # Обновляем пароль, если указан новый
        new_password = request.POST.get("new_password", "")
        if new_password:
            if len(new_password) < 8:
                messages.error(request, "Пароль должен быть не менее 8 символов")
                return redirect("employee_profile")
            user.set_password(new_password)

        user.save()

        messages.success(request, "Профиль успешно обновлен")
        # Перелогиниваем, если изменили пароль
        if new_password:
            from django.contrib.auth import update_session_auth_hash

            update_session_auth_hash(request, user)

        return redirect("employee_profile")

    return render(request, "users/employee_profile.html", {"user": request.user})


@csrf_protect
@require_POST  # Только POST запросы
@login_required
def custom_logout(request):
    """Кастомный выход из системы для надежности"""
    # Очищаем все сессионные флаги перед выходом
    session_keys_to_remove = ["show_site_for_admin", "force_site", "admin_override"]

    for key in session_keys_to_remove:
        if key in request.session:
            del request.session[key]

    # Получаем имя пользователя для логов
    username = request.user.username

    # Выполняем выход
    auth_logout(request)

    # Полностью очищаем сессию
    request.session.flush()

    # Логируем выход
    print(f"Пользователь {username} вышел из системы")

    # Редирект на главную с параметром для сброса логики smart_home_redirect
    return redirect("/?just_logged_out=true")


# Альтернативная версия для GET запросов (если нужно)
def logout_confirm(request):
    """Страница подтверждения выхода"""
    if not request.user.is_authenticated:
        return redirect("/")

    return render(request, "registration/logout_confirm.html")


# Простой выход без подтверждения
def simple_logout_view(request):
    """Простой выход (для GET запросов)"""
    if request.user.is_authenticated:
        auth_logout(request)
        request.session.flush()
    return redirect("/")
