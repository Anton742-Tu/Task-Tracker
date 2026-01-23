from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "role", "is_staff")
    list_filter = ("role", "is_staff", "is_superuser")

    # ignore для mypy ошибок с типами
    fieldsets = list(UserAdmin.fieldsets) + [  # type: ignore
        (
            _("Дополнительная информация"),
            {"fields": ("role", "bio", "avatar", "phone", "department", "position")},
        ),
    ]

    add_fieldsets = list(UserAdmin.add_fieldsets) + [  # type: ignore
        (_("Дополнительная информация"), {"fields": ("role",)}),
    ]

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

    actions = ["export_telegram_ids", "import_telegram_ids"]

    def export_telegram_ids(self, request, queryset):
        """Экспорт chat_id в CSV"""
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="telegram_ids.csv"'

        writer = csv.writer(response)
        writer.writerow(["username", "email", "telegram_chat_id"])

        for user in queryset:
            writer.writerow([user.username, user.email, user.telegram_chat_id or ""])

        return response

    export_telegram_ids.short_description = "Экспорт Telegram ID"
