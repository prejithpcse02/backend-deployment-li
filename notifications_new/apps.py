from django.apps import AppConfig


class NotificationsNewConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications_new'

    def ready(self):
        import notifications_new.signals
