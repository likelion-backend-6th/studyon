import os
from .base import *


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

CSRF_TRUSTED_ORIGINS = [
    "https://staging.limeskin.kr",
    "http://staging.limeskin.kr",
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


# Debug Toolbar Setting
INTERNAL_IPS = [
    "staging.limeskin.kr",
]

# Redis Cache Setting
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis-studyon-staging:6379/1",
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
            "hosts": [("redis-studyon-staging", 6379)],
        },
    },
}
