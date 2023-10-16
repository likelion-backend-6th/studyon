from celery import shared_task

from common.utils import filter_model_data_to_change_status, filter_model_data_to_delete
from manager.models import Study


@shared_task
def cleanup_old_studies():
    studies_to_delete = filter_model_data_to_delete(
        "manager", "Study", "updated_at", 30, "is_active", False, True
    )
    studies_to_delete.delete()


@shared_task
def cleanup_old_tasks():
    tasks_to_delete = filter_model_data_to_delete(
        "manager", "Task", "updated_at", 30, "is_active", False, True
    )
    tasks_to_delete.delete()


@shared_task
def cleanup_old_posts():
    posts_to_delete = filter_model_data_to_delete(
        "manager", "Post", "updated_at", 30, "is_active", False, True
    )
    posts_to_delete.delete()


@shared_task
def change_studies_status():
    studies_to_change = filter_model_data_to_change_status("manager", "Study", "end")
    studies_to_change.update(status=Study.Status.FINISHED)
