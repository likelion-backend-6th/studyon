import random

from django.core.management.base import BaseCommand

from faker import Faker

from manager.models import Study
from message.models import Message


# TODO: 커맨드 활용
# https://docs.djangoproject.com/en/4.2/howto/custom-management-commands/#testing
class Command(BaseCommand):
    help = "PUSH Message DB"

    def handle(self, *args, **options):
        created_msg_cnt = 0

        # chat_user
        def generate_random_message_users(study):
            members = study.members.all()
            chat_users = random.choices(members, k=2)
            return chat_users

        # sentence
        def generate_random_sentence():
            sentence = Faker(locale="en_US").sentence()
            return sentence

        # Create Task Objects
        studies = Study.objects.filter(is_active=True)
        for study in studies:
            print(f"study:{study}")
            try:
                msg_cnt = 0
                random_chat_cnt = random.randint(40, 100)
                while msg_cnt < random_chat_cnt:
                    chat_users = generate_random_message_users(study)
                    send_message = Message.objects.create(
                        sender=chat_users[0],
                        reciever=chat_users[1],
                        title=generate_random_sentence(),
                        content=generate_random_sentence(),
                    )
                    reply_message = Message.objects.create(
                        sender=chat_users[0],
                        reciever=chat_users[1],
                        title=generate_random_sentence(),
                        content=generate_random_sentence(),
                    )
                    msg_cnt += 2
                    created_msg_cnt += 2
                    print(f"{study.id}번 스터디에 {msg_cnt}개의 메세지가 생성되었습니다.")
                    print(f"{created_msg_cnt}개의 메세지가 생성되었습니다.")
            except:
                continue

        print(f"총 {created_msg_cnt}개의 메세지 생성을 완료하였습니다.")
