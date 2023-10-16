import os

from celery import Celery
from celery.schedules import crontab


ENV = os.getenv("RUN_MODE", "base")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"config.settings.{ENV}")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")


app.autodiscover_tasks()

app.conf.beat_schedule = {
    "clean_up_old_rooms": {
        "task": "chat.tasks.cleanup_old_rooms",
        "schedule": crontab(hour=0, minute=3),
    },
    "clean_up_old_studies": {
        "task": "manager.tasks.cleanup_old_studies",
        "schedule": crontab(hour=0, minute=4),
    },
    "clean_up_old_tasks": {
        "task": "manager.tasks.cleanup_old_tasks",
        "schedule": crontab(hour=0, minute=5),
    },
    "clean_up_old_posts": {
        "task": "manager.tasks.cleanup_old_posts",
        "schedule": crontab(hour=0, minute=6),
    },
    "clean_up_old_messagges": {
        "task": "message.tasks.cleanup_old_messagges",
        "schedule": crontab(hour=0, minute=7),
    },
    "clean_up_old_recruits": {
        "task": "recruit.tasks.cleanup_old_recruits",
        "schedule": crontab(hour=0, minute=8),
    },
    "change_finished_studies_status": {
        "task": "manager.tasks.change_studies_status",
        "schedule": crontab(hour=0, minute=9),
    },
    "change_finished_recruit_status": {
        "task": "recruit.tasks.change_recruits_status",
        "schedule": crontab(hour=0, minute=10),
    },
}
