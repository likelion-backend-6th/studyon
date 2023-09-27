import os
from .base import *


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")


ALLOWED_HOSTS = [
    os.getenv("DJANGO_DOMAIN"),
]


DEBUG = False


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


###### 추후 정적파일 서빙을 위해 미리 작성해둠

INSTALLED_APPS += [
    "storages",
]


# S3
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", "")
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com"
AWS_DEFAULT_ACL = "public-read"
DEFAULT_FILE_STORAGE = "config.storages.S3DefaultStorage"
STATICFILES_STORAGE = "config.storages.S3StaticStorage"
