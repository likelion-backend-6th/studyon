import random

from django.core.management.base import BaseCommand

from chat.models import Room
from manager.models import Study


# TODO: 커맨드 활용
# https://docs.djangoproject.com/en/4.2/howto/custom-management-commands/#testing
class Command(BaseCommand):
    help = "PUSH Room DB"

    def handle(self, *args, **options):
        created_room_cnt = 0

        # creator
        def generate_random_creator(study):
            members = study.members.all()
            creator = random.choice(members)
            return creator

        # category
        def get_random_category():
            random_cnt = random.randint(1, 4)
            category_list = Room.CategoryChoices.choices
            categories = random.choices(category_list, k=random_cnt)
            return categories

        # Create Room Objects
        studies = Study.objects.filter(is_active=True, status__lt=Study.Status.FINISHED)
        for study in studies:
            try:
                categories = get_random_category()
                for category in categories:
                    room, room_created = Room.objects.get_or_create(
                        study=study,
                        category=category[0],
                        closed_at=None,
                        defaults={"creator": generate_random_creator(study)},
                    )
                    if room_created:
                        created_room_cnt += 1
                        print(f"{created_room_cnt}개의 채팅방이 생성되었습니다.")
            except:
                continue

        print(f"총 {created_room_cnt}개의 채팅방 생성을 완료하였습니다.")
