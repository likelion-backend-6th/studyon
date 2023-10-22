from datetime import date, datetime, timedelta
import random

from django.core.management.base import BaseCommand
from django.db.models import F, Count
from django.contrib.auth.models import User

from faker import Faker

from recruit.models import Recruit, Register


# TODO: 커맨드 활용
# https://docs.djangoproject.com/en/4.2/howto/custom-management-commands/#testing
class Command(BaseCommand):
    help = "PUSH Register DB"

    def handle(self, *args, **options):
        created_register_cnt = 0

        start_date = date(2023, 8, 1)
        end_date = date(2024, 1, 31)

        # study
        def get_registable_recruits():
            registable_recruits = Recruit.objects.annotate(
                members_count=Count("members")
            ).filter(
                members_count__lt=F("total_seats"),
                study__status__lt=3,
                is_active=True,
            )
            return registable_recruits

        # title
        def get_exclude_recruit_members(recruit):
            recruit_members = recruit.members.all().values_list("id")
            not_registered_members = User.objects.exclude(members_recruits=recruit)
            return not_registered_members

        # users
        def get_random_users(users):
            total_users = users.count()
            random_user_cnt = random.randrange(1, total_users + 1)
            random_users = random.choices(list(users), k=random_user_cnt)
            return random_users

        # paragraph
        def generate_random_paragraph():
            paragraph = Faker(locale="en_US").paragraph()
            return paragraph

        # Create Register Objects
        registable_recruits = get_registable_recruits()
        for recruit in registable_recruits:
            registable_users = get_exclude_recruit_members(recruit)
            regist_users = get_random_users(registable_users)
            for user in regist_users:
                register, register_created = Register.objects.get_or_create(
                    recruit=recruit,
                    requester=user,
                    is_joined=None,
                    defaults={
                        "content": f"안녕하세요, {user}입니다. {recruit.id}번 모집에 참가신청합니다."
                    },
                )
                if register_created:
                    created_register_cnt += 1
                    print(f"{created_register_cnt}개의 참여 요청이 생성되었습니다.")

        print(f"총 {created_register_cnt}개의 참여 요청 생성을 완료하였습니다.")
