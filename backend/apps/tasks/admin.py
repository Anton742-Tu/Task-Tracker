from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Админка для задач."""

    list_display = ["title", "project", "assignee", "status", "priority", "due_date"]
    list_filter = ["status", "priority", "project", "assignee"]
    search_fields = ["title", "description"]
    readonly_fields = ["created_at", "updated_at", "creator"]
    date_hierarchy = "due_date"

    fieldsets = (
        (
            "Основная информация",
            {
                "fields": ("title", "description", "project", "assignee", "creator")
            },  # ← Добавили creator
        ),
        ("Статус и приоритет", {"fields": ("status", "priority")}),
        ("Сроки", {"fields": ("due_date",)}),
        ("Даты", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    # Автоматически заполняем создателя при создании задачи
    def save_model(self, request, obj, form, change):
        if not change:  # Только при создании новой задачи
            obj.creator = request.user
        super().save_model(request, obj, form, change)
