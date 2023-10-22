from datetime import date, datetime, timedelta
import random

from django.core.management.base import BaseCommand

from faker import Faker

from django.contrib.auth.models import User
from common.utils import Tags
from manager.models import Study
from recruit.models import Recruit, Register

from user.models import Profile


# TODO: 커맨드 활용
# https://docs.djangoproject.com/en/4.2/howto/custom-management-commands/#testing
class Command(BaseCommand):
    help = "PUSH USER DB"

    def handle(self, *args, **options):
        # 생성할 recruit/study 수
        number = int(input("생성할 모집/스터디 수를 입력하세요 :  "))
        created_rs_cnt = 0

        start_date = date(2023, 8, 1)
        end_date = date(2024, 1, 31)

        # creator
        def generate_random_user():
            total_user = User.objects.all()
            user = random.choice(list(total_user))
            return user

        # title
        def generate_random_title():
            subject = [
                "파이썬",
                "장고",
                "자바스크립트",
                "도커",
                "쿠버네티스",
                "GitHub Actions",
                "코딩테스트",
                "알고리즘",
                "CS",
            ]
            preposition = ["함께", "같이", "모여서"]
            verb = ["모집합니다", "구합니다", "모십니다", "연락주세요", "지원해주세요"]

            title = f"{random.choice(subject)} 스터디 {random.choice(preposition)} 하실 분 {random.choice(verb)}."

            return title

        # tags
        def generate_random_tags():
            tag_list = Tags.tag_list
            tag_cnt = random.randrange(1, 4)
            add_tag_list = random.choices(tag_list, k=tag_cnt)
            return add_tag_list

        # deadline
        def generate_random_deadline(start_date, end_date):
            deadline = Faker(locale="ko_KR").date_between_dates(start_date, end_date)
            return deadline

        # start, end
        def generate_random_start_and_end(deadline, end_date):
            result = random.choices(range(1, (end_date - deadline).days + 1), k=2)
            start = deadline + timedelta(min(result))
            end = deadline + timedelta(max(result))
            return start, end

        # total_seats
        def generate_random_total_seats():
            total_seats = random.randrange(2, 11)
            return total_seats

        # user_cnt
        def generate_random_user_cnt(maximum=10000):
            users = User.objects.exclude(username=creator.username)
            total_users = users.count()
            maximum = min(total_users, maximum)
            random_user_cnt = random.randrange(1, maximum + 1)
            return random_user_cnt

        # users
        def generate_random_users(num, creator):
            users = User.objects.exclude(username=creator.username)
            random_user_cnt = random.randrange(1, num + 1)
            random_users = set(random.choices(list(users), k=random_user_cnt))
            return random_users

        # paragraph
        def generate_random_paragraph():
            paragraph = Faker(locale="en_US").paragraph()
            return paragraph

        # Create Study & Recruit Objects
        while created_rs_cnt < number:
            creator = generate_random_user()
            title = generate_random_title()
            tags = generate_random_tags()
            deadline = generate_random_deadline(start_date, end_date)
            start, end = generate_random_start_and_end(deadline, end_date)
            total_seats = generate_random_total_seats()
            members = generate_random_users(
                generate_random_user_cnt(total_seats - 1), creator
            )
            target = generate_random_paragraph()
            process = generate_random_paragraph()
            info = generate_random_paragraph()
            like_users = generate_random_users(generate_random_user_cnt(), creator)
            created_at = datetime.combine(deadline - timedelta(10), datetime.min.time())
            updated_at = datetime.combine(end, datetime.min.time())

            today = date.today()

            if end < today:
                status = Study.Status.FINISHED
            elif start < today:
                status = Study.Status.IN_PROGRESS
            else:
                status = Study.Status.RECRUITING

            try:
                study, study_created = Study.objects.get_or_create(
                    creator=creator,
                    title=title,
                    start=start,
                    end=end,
                    process=process,
                    info=info,
                    status=status,
                )

                if study_created:
                    study.tags.add(*tags)
                    study.members.add(creator)
                    study.members.add(*members)

                    recruit, recruit_created = Recruit.objects.get_or_create(
                        study=study,
                        creator=creator,
                        title=title,
                        deadline=deadline,
                        start=start,
                        end=end,
                        total_seats=total_seats,
                        target=target,
                        process=process,
                        info=info,
                    )

                    if recruit_created:
                        recruit.tags.add(*tags)
                        recruit.members.add(creator)
                        recruit.members.add(*members)
                        recruit.like_users.add(*like_users)
                        print(f"creator:{creator}")
                        print(f"members:{members}")

                        for member in members:
                            Register.objects.get_or_create(
                                recruit=recruit,
                                requester=member,
                                is_joined=True,
                                defaults={
                                    "content": f"안녕하세요, {member}입니다. {recruit.id}번 모집에 참가신청합니다."
                                },
                            )
                            print(f"안녕하세요, {member}입니다. {recruit.id}번 모집에 참가신청합니다.")

                        study.created_at = created_at
                        study.updated_at = updated_at
                        study.save()

                        recruit.created_at = created_at
                        recruit.updated_at = updated_at
                        recruit.save()

                        created_rs_cnt += 1

                        print(f"{created_rs_cnt}개의 모집/스터디가 생성되었습니다.")
            except:
                continue

        print(f"총 {created_rs_cnt}개의 모집/스터디 생성을 완료하였습니다.")
