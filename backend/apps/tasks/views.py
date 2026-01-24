from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from datetime import date
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST

from .models import Task
from apps.projects.models import Project
from apps.users.models import User
from django.db import models


def admin_required(view_func):
    """Декоратор для проверки прав администратора"""

    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("/employee/login/")
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, "❌ У вас нет прав для выполнения этого действия")
            return redirect("/dashboard/")
        return view_func(request, *args, **kwargs)

    return wrapper


@login_required
@admin_required
def create_task(request):
    """Создание новой задачи (только для админов)"""
    if request.method == "POST":
        try:
            # Получаем данные из формы
            title = request.POST.get("title", "").strip()
            description = request.POST.get("description", "").strip()
            project_id = request.POST.get("project")
            assignee_id = request.POST.get("assignee")
            due_date_str = request.POST.get("due_date")
            priority = request.POST.get("priority", Task.Priority.MEDIUM)

            # Валидация
            if not title:
                messages.error(request, "❌ Название задачи обязательно")
                return redirect("tasks:create_task")

            if not project_id:
                messages.error(request, "❌ Необходимо выбрать проект")
                return redirect("tasks:create_task")

            # Получаем проект
            try:
                project = Project.objects.get(id=project_id)
            except (Project.DoesNotExist, ValueError):
                messages.error(request, "❌ Проект не найден")
                return redirect("tasks:create_task")

            # Создаем задачу
            task = Task.objects.create(
                title=title,
                description=description,
                project=project,
                creator=request.user,
                priority=priority,
                status=Task.Status.TODO,
            )

            # Назначаем исполнителя
            if assignee_id:
                try:
                    assignee = User.objects.get(id=assignee_id)
                    task.assignee = assignee
                    task.save()
                except (User.DoesNotExist, ValueError):
                    messages.warning(
                        request,
                        "⚠️ Исполнитель не найден, задача сохранена без исполнителя",
                    )

            # Устанавливаем срок
            if due_date_str:
                try:
                    task.due_date = timezone.datetime.strptime(
                        due_date_str, "%Y-%m-%d"
                    ).date()
                    task.save()
                except ValueError:
                    messages.warning(request, "⚠️ Неверный формат даты")

            # Успешное сообщение
            if task.assignee:
                messages.success(
                    request,
                    f'✅ Задача "{title}" создана успешно! '
                    f"Проект: {project.name}, "
                    f"Исполнитель: {task.assignee.get_full_name() or task.assignee.username}",
                )
            else:
                messages.success(
                    request,
                    f'✅ Задача "{title}" создана успешно! Проект: {project.name}',
                )

            # Редирект в зависимости от пользователя
            if request.user.is_superuser or request.user.is_staff:
                return redirect("/admin/tasks/task/")
            else:
                return redirect("/dashboard/")

        except Exception as e:
            messages.error(request, f"❌ Ошибка при создании задачи: {str(e)}")
            return redirect("tasks:create_task")

    # GET запрос - показываем форму
    try:
        projects = Project.objects.all()
        users = User.objects.filter(is_active=True).order_by(
            "first_name", "last_name", "username"
        )
    except Exception as e:
        messages.warning(request, f"⚠️ Ошибка загрузки данных: {str(e)}")
        projects = []
        users = []

    context = {
        "projects": projects,
        "users": users,
        "today": date.today(),
        "status_choices": Task.Status.choices,
        "priority_choices": Task.Priority.choices,
    }

    return render(request, "tasks/create_task.html", context)


@login_required
def task_list(request):
    """Список задач (разный для админов и сотрудников)"""
    try:
        if request.user.is_superuser or request.user.is_staff:
            # Админы видят все задачи
            tasks = Task.objects.all().order_by("-created_at")
            view_type = "all"
        else:
            # Сотрудники видят задачи, где они исполнитель или создатель
            tasks = Task.objects.filter(
                models.Q(assignee=request.user) | models.Q(creator=request.user)
            ).order_by("-created_at")
            view_type = "my"

        # Фильтрация по статусу
        status_filter = request.GET.get("status")
        if status_filter and status_filter != "all":
            tasks = tasks.filter(status=status_filter)

        # Фильтрация по проекту
        project_filter = request.GET.get("project")
        if project_filter and project_filter != "all":
            tasks = tasks.filter(project_id=project_filter)

        # Поиск
        search_query = request.GET.get("q")
        if search_query:
            tasks = tasks.filter(title__icontains=search_query)

        # Статистика
        total_tasks = tasks.count()
        active_tasks = tasks.exclude(status=Task.Status.DONE).count()
        completed_tasks = tasks.filter(status=Task.Status.DONE).count()

        # Получаем доступные проекты для фильтра
        available_projects = Project.objects.filter(
            id__in=tasks.values_list("project", flat=True).distinct()
        )

        context = {
            "tasks": tasks,
            "view_type": view_type,
            "total_tasks": total_tasks,
            "active_tasks": active_tasks,
            "completed_tasks": completed_tasks,
            "status_filter": status_filter or "all",
            "project_filter": project_filter or "all",
            "search_query": search_query or "",
            "available_projects": available_projects,
            "status_choices": Task.Status.choices,
            "priority_choices": Task.Priority.choices,
            "today": timezone.now().date(),
        }

        return render(request, "tasks/task_list.html", context)

    except Exception as e:
        messages.error(request, f"❌ Ошибка загрузки задач: {str(e)}")
        return redirect("/dashboard/")


@login_required
def task_detail(request, task_id):
    """Детали задачи"""
    try:
        task = get_object_or_404(Task, id=task_id)

        # Проверяем доступ
        if not (
            request.user.is_superuser
            or request.user.is_staff
            or task.assignee == request.user
            or task.creator == request.user
        ):
            messages.error(request, "❌ У вас нет доступа к этой задаче")
            return redirect("/dashboard/")

        # Изменение статуса
        if request.method == "POST" and "change_status" in request.POST:
            new_status = request.POST.get("new_status")
            if new_status in dict(Task.Status.choices):
                task.status = new_status
                task.save()
                messages.success(
                    request,
                    f"✅ Статус изменен на: {dict(Task.Status.choices)[new_status]}",
                )
                return redirect("tasks:task_detail", task_id=task.id)

        # Комментарии (если будут)
        comments = []

        context = {
            "task": task,
            "comments": comments,
            "status_choices": Task.Status.choices,
            "priority_choices": Task.Priority.choices,
            "today": timezone.now().date(),
            "can_edit": request.user.is_superuser
            or request.user.is_staff
            or request.user == task.creator,
        }

        return render(request, "tasks/task_detail.html", context)

    except Exception as e:
        messages.error(request, f"❌ Ошибка: {str(e)}")
        return redirect("/dashboard/")


@login_required
def edit_task(request, task_id):
    """Редактирование задачи"""
    try:
        task = get_object_or_404(Task, id=task_id)

        # Проверяем права на редактирование
        if not (
            request.user.is_superuser
            or request.user.is_staff
            or request.user == task.creator
        ):
            messages.error(request, "❌ У вас нет прав для редактирования этой задачи")
            return redirect("tasks:task_detail", task_id=task_id)

        if request.method == "POST":
            # Обновляем данные задачи
            task.title = request.POST.get("title", task.title).strip()
            task.description = request.POST.get("description", task.description).strip()
            task.priority = request.POST.get("priority", task.priority)
            task.status = request.POST.get("status", task.status)

            # Проект
            project_id = request.POST.get("project")
            if project_id:
                try:
                    task.project = Project.objects.get(id=project_id)
                except (Project.DoesNotExist, ValueError):
                    messages.error(request, "❌ Проект не найден")
                    return redirect("tasks:edit_task", task_id=task_id)

            # Исполнитель
            assignee_id = request.POST.get("assignee")
            if assignee_id:
                try:
                    task.assignee = User.objects.get(id=assignee_id)
                except (User.DoesNotExist, ValueError):
                    task.assignee = None
            else:
                task.assignee = None

            # Срок
            due_date_str = request.POST.get("due_date")
            if due_date_str:
                try:
                    task.due_date = timezone.datetime.strptime(
                        due_date_str, "%Y-%m-%d"
                    ).date()
                except ValueError:
                    task.due_date = None
            else:
                task.due_date = None

            task.save()
            messages.success(request, f'✅ Задача "{task.title}" обновлена успешно!')
            return redirect("tasks:task_detail", task_id=task.id)

        # GET запрос - показываем форму редактирования
        projects = Project.objects.all()
        users = User.objects.filter(is_active=True).order_by(
            "first_name", "last_name", "username"
        )

        context = {
            "task": task,
            "projects": projects,
            "users": users,
            "status_choices": Task.Status.choices,
            "priority_choices": Task.Priority.choices,
            "today": date.today(),
        }

        return render(request, "tasks/edit_task.html", context)

    except Exception as e:
        messages.error(request, f"❌ Ошибка при редактировании задачи: {str(e)}")
        return redirect("tasks:task_list")


@login_required
@admin_required
def delete_task(request, task_id):
    """Удаление задачи (только для админов)"""
    try:
        task = get_object_or_404(Task, id=task_id)

        if request.method == "POST":
            task_title = task.title
            task.delete()
            messages.success(request, f'✅ Задача "{task_title}" удалена успешно!')
            return redirect("tasks:task_list")

        # GET запрос - показываем подтверждение
        return render(request, "tasks/confirm_delete.html", {"task": task})

    except Exception as e:
        messages.error(request, f"❌ Ошибка при удалении задачи: {str(e)}")
        return redirect("tasks:task_list")


@login_required
@require_POST
def change_task_status(request, task_id):
    """Быстрое изменение статуса задачи (AJAX)"""
    try:
        task = get_object_or_404(Task, id=task_id)
        new_status = request.POST.get("status")

        # Проверяем права
        if not (
            request.user.is_superuser
            or request.user.is_staff
            or task.assignee == request.user
        ):
            return JsonResponse(
                {
                    "success": False,
                    "error": "У вас нет прав для изменения статуса этой задачи",
                },
                status=403,
            )

        # Проверяем валидность статуса
        if new_status not in dict(Task.Status.choices):
            return JsonResponse({"success": False, "error": "Неверный статус"})

        # Обновляем статус
        old_status_display = dict(Task.Status.choices)[task.status]
        task.status = new_status
        task.save()
        new_status_display = dict(Task.Status.choices)[task.status]

        return JsonResponse(
            {
                "success": True,
                "task_id": task_id,
                "new_status": new_status,
                "new_status_display": new_status_display,
                "old_status_display": old_status_display,
                "message": f"Статус изменен: {old_status_display} → {new_status_display}",
            }
        )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
def my_tasks(request):
    """Мои задачи (для сотрудников)"""
    try:
        # Задачи, где пользователь исполнитель
        assigned_tasks = Task.objects.filter(assignee=request.user).order_by(
            "-created_at"
        )

        # Задачи, созданные пользователем
        created_tasks = Task.objects.filter(creator=request.user).order_by(
            "-created_at"
        )

        # Объединяем и убираем дубликаты
        task_ids = set(assigned_tasks.values_list("id", flat=True))
        task_ids.update(created_tasks.values_list("id", flat=True))
        tasks = Task.objects.filter(id__in=task_ids).order_by("-created_at")

        # Статистика
        stats = {
            "total": tasks.count(),
            "todo": tasks.filter(status=Task.Status.TODO).count(),
            "in_progress": tasks.filter(status=Task.Status.IN_PROGRESS).count(),
            "review": tasks.filter(status=Task.Status.REVIEW).count(),
            "done": tasks.filter(status=Task.Status.DONE).count(),
            "blocked": tasks.filter(status=Task.Status.BLOCKED).count(),
        }

        # Просроченные задачи
        stats["overdue"] = tasks.filter(
            due_date__lt=timezone.now().date(),
            status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS, Task.Status.REVIEW],
        ).count()

        # Задачи по приоритету
        stats["critical"] = tasks.filter(priority=Task.Priority.CRITICAL).count()
        stats["high"] = tasks.filter(priority=Task.Priority.HIGH).count()
        stats["medium"] = tasks.filter(priority=Task.Priority.MEDIUM).count()
        stats["low"] = tasks.filter(priority=Task.Priority.LOW).count()

        context = {
            "tasks": tasks,
            "assigned_tasks": assigned_tasks,
            "created_tasks": created_tasks,
            "stats": stats,
            "status_choices": Task.Status.choices,
            "priority_choices": Task.Priority.choices,
            "today": timezone.now().date(),
        }

        return render(request, "tasks/my_tasks.html", context)

    except Exception as e:
        messages.error(request, f"❌ Ошибка загрузки задач: {str(e)}")
        return redirect("/dashboard/")


@login_required
def task_statistics(request):
    """Статистика по задачам"""
    try:
        if request.user.is_superuser or request.user.is_staff:
            # Админы видят статистику по всем задачам
            tasks = Task.objects.all()
        else:
            # Сотрудники видят статистику по своим задачам
            tasks = Task.objects.filter(
                models.Q(assignee=request.user) | models.Q(creator=request.user)
            )

        # Статистика по статусам
        status_stats = {}
        for status_code, status_name in Task.Status.choices:
            status_stats[status_code] = {
                "name": status_name,
                "count": tasks.filter(status=status_code).count(),
                "percentage": 0,
            }

        # Статистика по приоритетам
        priority_stats = {}
        for priority_code, priority_name in Task.Priority.choices:
            priority_stats[priority_code] = {
                "name": priority_name,
                "count": tasks.filter(priority=priority_code).count(),
                "percentage": 0,
            }

        total_tasks = tasks.count()

        # Рассчитываем проценты
        if total_tasks > 0:
            for stat in status_stats.values():
                stat["percentage"] = round((stat["count"] / total_tasks) * 100, 1)

            for stat in priority_stats.values():
                stat["percentage"] = round((stat["count"] / total_tasks) * 100, 1)

        # Просроченные задачи
        overdue_tasks = tasks.filter(
            due_date__lt=timezone.now().date(),
            status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS, Task.Status.REVIEW],
        ).count()

        # Задачи без исполнителя
        unassigned_tasks = tasks.filter(assignee__isnull=True).count()

        # Последние обновленные задачи
        recent_tasks = tasks.order_by("-updated_at")[:10]

        context = {
            "total_tasks": total_tasks,
            "status_stats": status_stats,
            "priority_stats": priority_stats,
            "overdue_tasks": overdue_tasks,
            "unassigned_tasks": unassigned_tasks,
            "recent_tasks": recent_tasks,
            "today": timezone.now().date(),
        }

        return render(request, "tasks/statistics.html", context)

    except Exception as e:
        messages.error(request, f"❌ Ошибка загрузки статистики: {str(e)}")
        return redirect("/dashboard/")
