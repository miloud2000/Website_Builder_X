from django.apps import AppConfig

class WebsitebuilderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'websitebuilder'

    def ready(self):
        import websitebuilder.signals
