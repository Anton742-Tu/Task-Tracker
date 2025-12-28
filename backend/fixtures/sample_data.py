"""
Скрипт для создания тестовых данных
Запуск: python manage.py shell < fixtures/sample_data.py
"""

import os

import django
from django.contrib.auth import get_user_model

from apps.projects.models import Project
from apps.tasks.models import Task

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


User = get_user_model()

# Создаем тестового пользователя
if not User.objects.filter(username="admin").exists():
    admin_user = User.objects.create_superuser(
        username="admin", email="admin@example.com", password="admin123"
    )
    print("Создан суперпользователь: admin/admin123")

# Создаем обычных пользователей
if not User.objects.filter(username="manager").exists():
    manager = User.objects.create_user(
        username="manager",
        email="manager@example.com",
        password="manager123",
        first_name="Иван",
        last_name="Менеджеров",
    )
    print("Создан менеджер: manager/manager123")

if not User.objects.filter(username="employee").exists():
    employee = User.objects.create_user(
        username="employee",
        email="employee@example.com",
        password="employee123",
        first_name="Петр",
        last_name="Сотрудников",
    )
    print("Создан сотрудник: employee/employee123")

# Создаем проекты
projects_data = [
    {
        "name": "Разработка нового сайта",
        "description": "Создание корпоративного сайта компании",
        "status": "active",
        "creator": User.objects.get(username="admin"),
    },
    {
        "name": "Мобильное приложение",
        "description": "Разработка iOS и Android приложения",
        "status": "active",
        "creator": User.objects.get(username="manager"),
    },
    {
        "name": "Перенос на новый сервер",
        "description": "Миграция инфраструктуры в облако",
        "status": "inactive",
        "creator": User.objects.get(username="admin"),
    },
]

for project_data in projects_data:
    project, created = Project.objects.get_or_create(
        name=project_data["name"], defaults=project_data
    )
    if created:
        # Добавляем участников
        project.members.add(project_data["creator"])
        if project_data["creator"].username == "admin":
            project.members.add(User.objects.get(username="manager"))
        print(f"Создан проект: {project.name}")

# Создаем задачи
tasks_data = [
    {
        "title": "Дизайн главной страницы",
        "description": "Создать макет главной страницы сайта",
        "project": Project.objects.get(name="Разработка нового сайта"),
        "status": "in_progress",
    },
    {
        "title": "API для мобильного приложения",
        "description": "Разработать REST API для iOS/Android",
        "project": Project.objects.get(name="Мобильное приложение"),
        "status": "todo",
    },
    {
        "title": "Настройка сервера",
        "description": "Установить и настроить серверное ПО",
        "project": Project.objects.get(name="Перенос на новый сервер"),
        "status": "completed",
    },
    {
        "title": "Тестирование API",
        "description": "Написать тесты для API endpoints",
        "project": Project.objects.get(name="Мобильное приложение"),
        "status": "in_progress",
    },
]

for task_data in tasks_data:
    task, created = Task.objects.get_or_create(
        title=task_data["title"], defaults=task_data
    )
    if created:
        print(f"Создана задача: {task.title}")

print("Тестовые данные созданы успешно!")
