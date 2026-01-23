from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


def enable_telegram_notifications(modeladmin, request, queryset):
    """Включить Telegram уведомления для выбранных пользователей"""
    queryset.update(telegram_notifications=True)
    modeladmin.message_user(
        request, f"Уведомления включены для {queryset.count()} пользователей"
    )


enable_telegram_notifications.short_description = "Включить Telegram уведомления"  # type: ignore


def disable_telegram_notifications(modeladmin, request, queryset):
    """Выключить Telegram уведомления для выбранных пользователей"""
    queryset.update(telegram_notifications=False)
    modeladmin.message_user(
        request, f"Уведомления выключены для {queryset.count()} пользователей"
    )


disable_telegram_notifications.short_description = "Выключить Telegram уведомления"  # type: ignore


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_staff",
        "has_telegram",
    )
    list_filter = ("role", "is_staff", "is_superuser", "telegram_notifications")

    # Добавляем действия ДО объявления класса или внутри него
    actions = [enable_telegram_notifications, disable_telegram_notifications]

    # Полное переопределение
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (
            _("Дополнительная информация"),
            {"fields": ("role", "bio", "avatar", "phone", "department", "position")},
        ),
        (
            _("Telegram настройки"),
            {
                "fields": (
                    "telegram_username",
                    "telegram_chat_id",
                    "telegram_notifications",
                    "telegram_linked_at",
                ),
                "classes": ("collapse",),  # Сворачиваемый раздел
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "email"),
            },
        ),
        (
            _("Дополнительная информация"),
            {
                "classes": ("wide",),
                "fields": ("role",),
            },
        ),
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

    # Добавляем кастомные методы
    def has_telegram(self, obj):
        """Проверяет, привязан ли Telegram"""
        return bool(obj.telegram_chat_id)

    has_telegram.boolean = True  # type: ignore
    has_telegram.short_description = "Telegram"  # type: ignore

    def get_telegram_info(self, obj):
        """Информация о Telegram"""
        if obj.telegram_chat_id:
            info = f"ID: {obj.telegram_chat_id}"
            if obj.telegram_username:
                info += f" (@{obj.telegram_username})"
            if not obj.telegram_notifications:
                info += " 🔕"
            return info
        return "—"

    get_telegram_info.short_description = "Telegram информация"  # type: ignore
