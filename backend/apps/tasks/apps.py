from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.tasks"
    verbose_name = "Задачи"

    def ready(self):
        print("🔄 TasksConfig.ready() вызывается...")
        import apps.tasks.signals

        print("✅ Сигналы подключены")
