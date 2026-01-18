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

    def get_queryset(self, request):
        """Менеджеры видят только свои проекты"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(creator=request.user) | qs.filter(members=request.user)

    def has_change_permission(self, request, obj=None):
        """Менеджеры могут редактировать только свои проекты"""
        if obj and not request.user.is_superuser:
            return obj.creator == request.user or request.user in obj.members.all()
        return super().has_change_permission(request, obj)
