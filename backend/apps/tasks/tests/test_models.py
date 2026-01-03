from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.projects.models import Project
from apps.tasks.models import Task

User = get_user_model()


class TaskModelTestCase(TestCase):
    """Тесты для модели Task"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.project = Project.objects.create(
            name="Test Project",
            description="Description",
            status="active",
            creator=self.user,
        )

        self.task = Task.objects.create(
            title="Test Task",
            description="Task Description",
            project=self.project,
            status="todo",
            priority="medium",
            due_date=date.today() + timedelta(days=7),
            creator=self.user,
            assignee=self.user,
        )

    def test_task_creation(self):
        """Тест создания задачи"""
        self.assertEqual(self.task.title, "Test Task")
        self.assertEqual(self.task.status, "todo")
        self.assertEqual(self.task.priority, "medium")
        self.assertEqual(self.task.creator, self.user)
        self.assertEqual(self.task.assignee, self.user)

    def test_task_str_method(self):
        """Тест строкового представления"""
        expected = "Task: Test Task (todo)"
        self.assertEqual(str(self.task), expected)

    def test_task_is_overdue(self):
        """Тест определения просроченной задачи"""
        # Непросроченная задача
        self.assertFalse(self.task.is_overdue)

        # Просроченная задача
        overdue_task = Task.objects.create(
            title="Overdue Task",
            description="Description",
            project=self.project,
            status="todo",
            due_date=date.today() - timedelta(days=1),
            creator=self.user,
        )

        self.assertTrue(overdue_task.is_overdue)

    def test_task_status_choices(self):
        """Тест допустимых значений статуса"""
        valid_statuses = ["todo", "in_progress", "completed", "cancelled"]

        for status in valid_statuses:
            task = Task.objects.create(
                title=f"Task {status}",
                description="Description",
                project=self.project,
                status=status,
                creator=self.user,
            )
            self.assertEqual(task.status, status)

    def test_task_priority_choices(self):
        """Тест допустимых значений приоритета"""
        valid_priorities = ["low", "medium", "high", "critical"]

        for priority in valid_priorities:
            task = Task.objects.create(
                title=f"Task {priority}",
                description="Description",
                project=self.project,
                status="todo",
                priority=priority,
                creator=self.user,
            )
            self.assertEqual(task.priority, priority)
