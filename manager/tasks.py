from celery import shared_task

from common.utils import filter_model_data_to_delete


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
