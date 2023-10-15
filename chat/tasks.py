from celery import shared_task

from common.utils import filter_model_data_to_delete


@shared_task
def cleanup_old_rooms():
    rooms_to_delete = filter_model_data_to_delete(
        "chat", "Room", "closed_at", 30, "closed_at", None, False
    )
    rooms_to_delete.delete()
