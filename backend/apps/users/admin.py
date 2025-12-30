from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "role", "is_staff")
    list_filter = ("role", "is_staff", "is_superuser")
    fieldsets = UserAdmin.fieldsets + (
        ("Дополнительная информация", {"fields": ("role", "bio", "avatar")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Дополнительная информация", {"fields": ("role",)}),
    )

    def get_queryset(self, request):
        """Менеджеры видят всех пользователей, но не могут редактировать админов"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Менеджеры видят всех, кроме суперпользователей
        return qs.filter(is_superuser=False)

    def has_change_permission(self, request, obj=None):
        """Менеджеры не могут менять других менеджеров и админов"""
        if obj and obj.is_superuser:
            return False
        if obj and obj.role == "manager" and obj != request.user:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """Менеджеры не могут удалять пользователей"""
        return False
