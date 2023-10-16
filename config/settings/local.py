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


# Celery Apps
INSTALLED_APPS += [
    "django_celery_results",
    "django_celery_beat",
]


# Redis Cache Setting
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}


# Channel Layer Settings
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)],
        },
    },
}


# Celery Settings
CELERY_TIMEZONE = "Asia/Seoul"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_RESULT_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"

CELERY_RESULT_BACKEND = "django-db"
CELERY_CACHE_BACKEND = "default"
CELERY_BROKER_URL = "redis://redis:6379/2"

# CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
