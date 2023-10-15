from celery import shared_task

from common.utils import filter_model_data_to_delete


@shared_task
def cleanup_old_recruits():
    recruits_to_delete = filter_model_data_to_delete(
        "recruit", "Recruit", "updated_at", 30, "is_active", False, True
    )
    recruits_to_delete.delete()
