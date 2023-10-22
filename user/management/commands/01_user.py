import random
import string

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from faker import Faker

from user.models import Profile


# TODO: 커맨드 활용
# https://docs.djangoproject.com/en/4.2/howto/custom-management-commands/#testing
class Command(BaseCommand):
    help = "PUSH USER DB"

    def handle(self, *args, **options):
        # 생성할 user 수
        number = int(input("생성할 유저 수를 입력하세요 :  "))
        created_user_cnt = 0

        # username
        def generate_random_username():
            username_length = random.randrange(5, 11)
            special_chars = "@.+-_"
            special_char_cnt = 0
            username = random.choice(string.ascii_lowercase)
            while len(username) < username_length:
                add_char = random.choice(
                    string.ascii_lowercase + string.digits + special_chars
                )
                if add_char in special_chars:
                    if special_char_cnt == 0:
                        special_char_cnt += 1
                    else:
                        continue
                username += add_char
            return username

        # nickname
        def generate_random_korean_nickname():
            nickname = Faker(locale="ko_KR").name()

            return nickname

        # password
        new_password = make_password("1234")

        # Create User objects
        while created_user_cnt < number:
            username = generate_random_username()
            nickname = generate_random_korean_nickname()
            password = new_password
            try:
                user, user_created = User.objects.get_or_create(
                    username=username, password=password
                )

                if user_created:
                    profile, profile_created = Profile.objects.get_or_create(
                        user=user, nickname=nickname
                    )

                    if profile_created:
                        created_user_cnt += 1

                        print(f"{created_user_cnt}명의 유저 계정이 생성되었습니다.")
            except:
                continue

        print(f"총 {created_user_cnt}명의 유저 계정 생성을 완료하였습니다.")
