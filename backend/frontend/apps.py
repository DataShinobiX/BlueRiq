# backend/frontend/apps.py
from django.apps import AppConfig

class FrontendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'frontend'  # use the correct full module path if needed

    def ready(self):
        # Import the dash app so that it's registered with DjangoPlotlyDash
        from . import dash_apps
