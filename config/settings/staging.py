import os
from .base import *


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")


ALLOWED_HOSTS = [
    os.getenv("DJANGO_DOMAIN"),
]


DEBUG = True


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "postgres"),
        "USER": os.getenv("POSTGRES_USER", "postgres"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "HOST": os.getenv("DB_HOST", "postgres"),
        "OPTIONS": {"options": "-c search_path=studyon,public"},
    }
}
