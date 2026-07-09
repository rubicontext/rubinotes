"""Point d'entrée WSGI pour uWSGI (déploiement sur lula)."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rubinotes.settings")

application = get_wsgi_application()
