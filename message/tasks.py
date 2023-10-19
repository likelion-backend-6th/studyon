from celery import shared_task

from common.utils import filter_model_data_to_delete


@shared_task
def cleanup_old_messages():
    messages_to_delete = filter_model_data_to_delete(
        "message", "Message", "read_at", 30, "read_at", None, False
    )
    messages_to_delete.delete()


@shared_task
def cleanup_old_notices():
    notices_to_delete = filter_model_data_to_delete(
        "message", "Message", "created_at", 30, "created_at", None, False
    )
    notices_to_delete.delete()
