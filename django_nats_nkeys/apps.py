from django.apps import AppConfig


class DjangoNatsNkeysConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_nats_nkeys"

    def ready(self):
        try:
            import django_nats_nkeys.signals  # noqa F401
        except ImportError:
            pass
