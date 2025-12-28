from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Админка для задач."""

    list_display = ["title", "project", "assignee", "status", "priority", "due_date"]
    list_filter = ["status", "priority", "project", "assignee"]
    search_fields = ["title", "description"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "due_date"

    fieldsets = (
        (
            "Основная информация",
            {"fields": ("title", "description", "project", "assignee")},
        ),
        ("Статус и приоритет", {"fields": ("status", "priority")}),
        ("Сроки", {"fields": ("due_date",)}),
        ("Даты", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
