from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Task
from apps.projects.models import Project
from apps.users.models import User


@login_required
def create_task(request):
    """Создание новой задачи"""
    if request.method == "POST":
        try:
            # Получаем данные из формы
            title = request.POST.get("title")
            description = request.POST.get("description")
            project_id = request.POST.get("project")
            assignee_id = request.POST.get("assignee")
            due_date = request.POST.get("due_date")
            priority = request.POST.get("priority", "medium")

            # Создаем задачу
            task = Task.objects.create(
                title=title,
                description=description,
                creator=request.user,
                priority=priority,
            )

            # Устанавливаем проект
            if project_id:
                try:
                    project = Project.objects.get(id=project_id)
                    task.project = project
                except Project.DoesNotExist:
                    pass

            # Назначаем исполнителя
            if assignee_id:
                try:
                    assignee = User.objects.get(id=assignee_id)
                    task.assignee = assignee
                except User.DoesNotExist:
                    pass

            # Устанавливаем срок
            if due_date:
                from datetime import datetime

                task.due_date = datetime.strptime(due_date, "%Y-%m-%d").date()

            task.save()
            messages.success(request, f'Задача "{title}" создана успешно!')
            return redirect("/dashboard/")

        except Exception as e:
            messages.error(request, f"Ошибка при создании задачи: {str(e)}")

    # Получаем список проектов и пользователей для формы
    projects = Project.objects.all()
    users = User.objects.filter(is_active=True).exclude(id=request.user.id)

    return render(
        request,
        "tasks/create_task.html",
        {
            "projects": projects,
            "users": users,
        },
    )
