from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "扩展内容"

    def ready(self):
        from . import admin_site  # noqa: F401