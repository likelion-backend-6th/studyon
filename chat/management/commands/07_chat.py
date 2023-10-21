import random

from django.core.management.base import BaseCommand

from faker import Faker

from chat.models import Chat, Room
from manager.models import Study


# TODO: 커맨드 활용
# https://docs.djangoproject.com/en/4.2/howto/custom-management-commands/#testing
class Command(BaseCommand):
    help = "PUSH Chat DB"

    def handle(self, *args, **options):
        created_chat_cnt = 0

        # chat_user
        def generate_random_chat_users(room):
            members = room.study.members.all()
            random_cnt = random.randint(2, members.count() + 1)
            chat_users = random.choices(members, k=random_cnt)
            return chat_users

        # sentence
        def generate_random_sentence():
            sentence = Faker(locale="en_US").sentence()
            return sentence

        # Create Task Objects
        studies = Study.objects.filter(is_active=True, status__lt=Study.Status.FINISHED)
        rooms = Room.objects.filter(study__in=studies, closed_at=None)
        for room in rooms:
            try:
                chat_cnt = 0
                random_chat_cnt = random.randint(10, 50)
                chat_users = generate_random_chat_users(room)
                while chat_cnt < random_chat_cnt:
                    creator = random.choice(chat_users)
                    content = generate_random_sentence()
                    chat, chat_created = Chat.objects.get_or_create(
                        room=room,
                        creator=creator,
                        content=content,
                    )
                    if chat_created:
                        chat_cnt += 1
                        created_chat_cnt += 1
                        print(f"{room.id}번 채팅방에 {chat_cnt}개의 채팅이 생성되었습니다.")
            except:
                continue

        print(f"총 {created_chat_cnt}개의 채팅 생성을 완료하였습니다.")
