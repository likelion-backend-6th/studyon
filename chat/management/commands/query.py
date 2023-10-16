from random import *

from django.core.management.base import BaseCommand

from common.utils import filter_model_data_to_change_status, filter_model_data_to_delete


# TODO: 커맨드 활용
# https://docs.djangoproject.com/en/4.2/howto/custom-management-commands/#testing
class Command(BaseCommand):
    help = "PUSH POST DB"

    def handle(self, *args, **options):
        rooms = filter_model_data_to_delete(
            "chat", "Room", "closed_at", 30, "closed_at", None, False
        )
        for room in rooms:
            print(room)

        tasks_to_delete = filter_model_data_to_delete(
            "manager", "Task", "updated_at", 30, "is_active", False, True
        )
        for task in tasks_to_delete:
            print(task)

        studies_to_change = filter_model_data_to_change_status(
            "manager", "Study", "end"
        )

        for study in studies_to_change:
            print(study)
