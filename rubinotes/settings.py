import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# En production, définir ces variables dans .env (cf. .env.example)
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-not-secret")
DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,*").split(",")

# Page privée /gouvernance : notes .md hors dépôt, protégées par mot de passe.
# Sans GOUV_PASSWORD, la page renvoie 404.
GOUV_PASSWORD = os.environ.get("GOUV_PASSWORD", "")
GOUV_DOCS_DIR = Path(os.environ.get("GOUV_DOCS_DIR", BASE_DIR / "private" / "gouvernance"))

INSTALLED_APPS = [
    "trainer",
]

MIDDLEWARE = []

ROOT_URLCONF = "rubinotes.urls"

WSGI_APPLICATION = "rubinotes.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": False,
        "OPTIONS": {
            # pas de cache en dev : le serveur tourne avec --noreload,
            # sans ça les modifs de template ne sont jamais rechargées
            "loaders": ["django.template.loaders.app_directories.Loader"]
            if DEBUG
            else [
                (
                    "django.template.loaders.cached.Loader",
                    ["django.template.loaders.app_directories.Loader"],
                )
            ],
        },
    },
]

# App sans état : aucune base de données
DATABASES = {}

USE_TZ = True
