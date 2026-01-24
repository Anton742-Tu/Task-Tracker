from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.notifications"
    verbose_name = "Уведомления"

    def ready(self):
        """Подключение сигналов для уведомлений"""
        # Если есть сигналы в этом приложении
        try:
            import apps.notifications.signals

            print("✅ Сигналы уведомлений подключены")
        except ImportError:
            pass  # Нет сигналов - это нормально
