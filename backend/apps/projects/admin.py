from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Админка для проектов."""

    list_display = ["name", "status", "creator", "get_members_display", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["name", "description"]
    filter_horizontal = ["members"]
    readonly_fields = ["created_at", "updated_at", "task_count", "completed_task_count"]

    fieldsets = (
        (
            "Основная информация",
            {"fields": ("name", "description", "status", "creator")},
        ),
        ("Участники", {"fields": ("members",)}),
        ("Даты", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
        (
            "Статистика",
            {
                "fields": ("task_count", "completed_task_count"),
                "classes": ("collapse",),
            },
        ),
    )
