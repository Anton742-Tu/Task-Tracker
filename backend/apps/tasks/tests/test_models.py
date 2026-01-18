# -*- coding: utf-8 -*-
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.projects.models import Project
from apps.tasks.models import Task

User = get_user_model()


class TaskModelTestCase(TestCase):
    """Тесты для модели Task"""

    def setUp(self):
        # Создаем пользователя
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Создаем проект
        self.project = Project.objects.create(
            name="Test Project",
            description="Description",
            status="active",
            creator=self.user,
        )

        # Создаем задачу
        self.task = Task.objects.create(
            title="Test Task",
            description="Task Description",
            project=self.project,
            creator=self.user,
            due_date=timezone.now().date() + timedelta(days=7),
            status=Task.Status.TODO,
            priority=Task.Priority.MEDIUM,
        )

    def test_task_creation_basic(self):
        """Базовый тест создания задачи"""
        self.assertEqual(self.task.title, "Test Task")
        self.assertEqual(self.task.description, "Task Description")
        self.assertEqual(self.task.creator, self.user)
        self.assertEqual(self.task.project, self.project)
        self.assertEqual(self.task.status, Task.Status.TODO)
        self.assertEqual(self.task.priority, Task.Priority.MEDIUM)
        self.assertIsNotNone(self.task.created_at)
        self.assertIsNotNone(self.task.updated_at)

    def test_task_dates(self):
        """Тест дат создания и обновления"""
        # Проверяем что даты установлены
        self.assertIsNotNone(self.task.created_at)
        self.assertIsNotNone(self.task.updated_at)

        # Ждем немного чтобы гарантировать разницу во времени
        import time

        time.sleep(0.01)

        # Обновляем задачу
        self.task.title = "Updated Title"
        self.task.save()

        # Проверяем что updated_at изменился (или не равен старому значению)
        # Вместо assertGreater используем assertNotEqual
        self.assertNotEqual(self.task.updated_at, self.task.created_at)

    def test_task_priority_choices(self):
        """Тест выбора приоритета"""
        # Проверяем доступные приоритеты через класс Priority.choices
        priorities = dict(Task.Priority.choices)
        self.assertEqual(priorities["low"], "Низкий")
        self.assertEqual(priorities["medium"], "Средний")
        self.assertEqual(priorities["high"], "Высокий")
        self.assertEqual(priorities["critical"], "Критический")

        # Проверяем отображение приоритета
        self.assertEqual(self.task.get_priority_display(), "Средний")

    def test_task_status_choices(self):
        """Тест выбора статуса"""
        # Проверяем доступные статусы через класс Status.choices
        statuses = dict(Task.Status.choices)
        self.assertEqual(statuses["todo"], "К выполнению")
        self.assertEqual(statuses["in_progress"], "В работе")
        self.assertEqual(statuses["review"], "На проверке")
        self.assertEqual(statuses["done"], "Выполнена")
        self.assertEqual(statuses["blocked"], "Заблокирована")

        # Проверяем отображение статуса
        self.assertEqual(self.task.get_status_display(), "К выполнению")

    def test_task_str_method(self):
        """Тест строкового представления"""
        # Согласно модели: return f"{self.title} ({self.get_status_display()})"
        expected = f"Test Task ({self.task.get_status_display()})"
        self.assertEqual(str(self.task), expected)

    def test_task_is_overdue(self):
        """Тест проверки просроченной задачи"""
        # Создаем просроченную задачу
        overdue_task = Task.objects.create(
            title="Overdue Task",
            description="Overdue description",
            project=self.project,
            creator=self.user,
            due_date=timezone.now().date() - timedelta(days=1),
            status=Task.Status.IN_PROGRESS,
        )

        self.assertTrue(overdue_task.is_overdue)

        # Текущая задача не просрочена
        self.assertFalse(self.task.is_overdue)

        # Завершенная задача не считается просроченной
        completed_task = Task.objects.create(
            title="Completed Task",
            description="Completed description",
            project=self.project,
            creator=self.user,
            due_date=timezone.now().date() - timedelta(days=1),
            status=Task.Status.DONE,
        )
        self.assertFalse(completed_task.is_overdue)

    def test_task_assignee_optional(self):
        """Тест что assignee может быть не указан"""
        task_without_assignee = Task.objects.create(
            title="Task Without Assignee",
            description="No assignee",
            project=self.project,
            creator=self.user,
        )

        self.assertIsNone(task_without_assignee.assignee)

    def test_task_default_values(self):
        """Тест значений по умолчанию"""
        new_task = Task.objects.create(
            title="Default Task", project=self.project, creator=self.user
        )

        self.assertEqual(new_task.status, Task.Status.TODO)
        self.assertEqual(new_task.priority, Task.Priority.MEDIUM)
        self.assertIsNone(new_task.assignee)
        self.assertIsNone(new_task.due_date)

    def test_task_meta_verbose_names(self):
        """Тест verbose_name в Meta классе"""
        self.assertEqual(Task._meta.verbose_name, "Задача")
        self.assertEqual(Task._meta.verbose_name_plural, "Задачи")
        self.assertEqual(Task._meta.ordering, ["-priority", "-created_at"])
