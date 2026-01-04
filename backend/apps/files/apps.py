from django.apps import AppConfig


class FilesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.files"
    verbose_name = "Файлы и вложения"

    def ready(self):
        """Импортируем сигналы при загрузке приложения"""
        try:
            import apps.files.signals  # noqa: F401
        except ImportError:
            pass
