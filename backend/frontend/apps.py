from django.apps import AppConfig

class FrontendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'frontend'  # or just 'frontend' if that's your module path

    def ready(self):
        # Import Dash apps here — after Django is fully initialized
        from . import dash_apps  
