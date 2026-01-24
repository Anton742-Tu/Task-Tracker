from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.tasks"
    verbose_name = "Задачи"

    def ready(self):
        """Подключение сигналов при запуске приложения"""
        # Импортируем сигналы только здесь, чтобы избежать циклических импортов
        import apps.tasks.signals

        print("✅ Сигналы задач подключены")
