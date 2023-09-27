from .base import *


CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
]


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
