from datetime import datetime
import random
from itertools import permutations

from django.core.management.base import BaseCommand

from faker import Faker

from manager.models import Post, Study, Task, File
from user.models import Review


# TODO: 커맨드 활용
# https://docs.djangoproject.com/en/4.2/howto/custom-management-commands/#testing
class Command(BaseCommand):
    help = "PUSH Review DB"

    def handle(self, *args, **options):
        created_review_cnt = 0

        # reviewers
        def generate_random_reviewers(members):
            if len(members) == 1:
                return list()
            total_reviewer_list = list(permutations(members, 2))
            random_reviewers_cnt = random.randint(1, len(total_reviewer_list) + 1)
            random_reviewers_list = random.choices(
                total_reviewer_list, k=random_reviewers_cnt
            )
            return random_reviewers_list

        # score
        def generate_random_score():
            return random.randrange(1, 11)

        # sentence
        def generate_random_sentence():
            sentence = Faker(locale="en_US").sentence()
            return sentence

        # Create Review Objects
        studies = Study.objects.filter(is_active=True, status__lt=Study.Status.FINISHED)
        for study in studies:
            print(f"study:{study}")
            try:
                members = study.members.all()
                reviewers = generate_random_reviewers(members)
                for review in reviewers:
                    reviewer = review[0]
                    reviewee = review[1]
                    score = generate_random_score()
                    review = generate_random_sentence()
                    review, review_created = Review.objects.get_or_create(
                        study=study,
                        reviewer=reviewer,
                        reviewee=reviewee,
                        defaults={"score": score, "review": review},
                    )
                    if review_created:
                        created_review_cnt += 1
                        print(f"{created_review_cnt}개의 review가 생성되었습니다.")
            except:
                continue

        print(f"총 {created_review_cnt}개의 review 생성을 완료하였습니다.")
