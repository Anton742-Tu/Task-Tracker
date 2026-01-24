from django import template
from django.utils.safestring import mark_safe
from ..models import Task

register = template.Library()


@register.filter
def can_complete_task(task, user):
    """Может ли пользователь завершить задачу"""
    if not user.is_authenticated:
        return False

    # Админы могут всё
    if user.is_superuser:
        return True

    # Исполнитель может завершить свою задачу
    if task.assignee == user:
        return True

    return False


@register.filter
def can_edit_task(task, user):
    """Может ли пользователь редактировать задачу"""
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    # Менеджеры могут редактировать задачи своих подчиненных
    if user.is_staff and task.assignee and task.assignee != user:
        return True

    # Создатель может редактировать
    if task.creator == user:
        return True

    return False


@register.filter
def task_status_color(status):
    """Возвращает цвет для статуса задачи"""
    color_map = {
        "todo": "secondary",  # 📋 К выполнению - серый
        "in_progress": "warning",  # ⚡ В работе - желтый
        "review": "info",  # 👀 На проверке - синий
        "done": "success",  # ✅ Выполнена - зеленый
        "blocked": "danger",  # 🚫 Заблокирована - красный
    }
    return color_map.get(status, "secondary")


@register.filter
def can_view_task(task, user):
    """Может ли пользователь просматривать задачу"""
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    # Сотрудник может видеть свои задачи
    if task.assignee == user:
        return True

    # Менеджер может видеть задачи своих подчиненных
    if user.is_staff and task.assignee:
        # Здесь можно добавить логику проверки, является ли task.assignee подчиненным
        return True

    # Создатель задачи может её видеть
    if task.creator == user:
        return True

    return False


@register.simple_tag
def get_task_badge(task):
    """Возвращает HTML бейдж для статуса задачи"""
    colors = {
        "todo": ("secondary", "📋 К выполнению"),
        "in_progress": ("warning", "⚡ В работе"),
        "review": ("info", "👀 На проверке"),
        "done": ("success", "✅ Выполнено"),
        "blocked": ("danger", "🚫 Заблокировано"),
    }

    color, text = colors.get(task.status, ("secondary", task.get_status_display()))

    return mark_safe(f'<span class="badge bg-{color}">{text}</span>')


@register.simple_tag
def get_priority_badge(task):
    """Возвращает HTML бейдж для приоритета задачи"""
    colors = {
        "low": ("secondary", "🔵 Низкий"),
        "medium": ("warning", "🟡 Средний"),
        "high": ("danger", "🔴 Высокий"),
        "critical": ("dark", "⚫ Критический"),
    }

    color, text = colors.get(task.priority, ("secondary", task.get_priority_display()))

    return mark_safe(f'<span class="badge bg-{color}">{text}</span>')


@register.filter
def is_task_overdue(task):
    """Просрочена ли задача"""
    from django.utils import timezone

    if not task.due_date:
        return False

    if task.status in ["done", "cancelled"]:
        return False

    return task.due_date < timezone.now().date()


@register.filter
def format_due_date(task):
    """Форматирует дату выполнения с подсветкой"""
    from django.utils import timezone
    from django.utils.safestring import mark_safe

    if not task.due_date:
        return "—"

    date_str = task.due_date.strftime("%d.%m.%Y")

    if task.status in ["done", "cancelled"]:
        return date_str

    if task.due_date < timezone.now().date():
        return mark_safe(f'<span class="text-danger">🚨 {date_str} (просрочено)</span>')
    elif task.due_date == timezone.now().date():
        return mark_safe(f'<span class="text-warning">⚠️ {date_str} (сегодня!)</span>')

    return date_str
