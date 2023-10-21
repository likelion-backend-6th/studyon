from datetime import datetime, timedelta
import random

from django.core.management.base import BaseCommand

from faker import Faker

from manager.models import Study, Task


# TODO: 커맨드 활용
# https://docs.djangoproject.com/en/4.2/howto/custom-management-commands/#testing
class Command(BaseCommand):
    help = "PUSH Task DB"

    def handle(self, *args, **options):
        created_task_cnt = 0

        # author
        def generate_random_author(study):
            members = study.members.all()
            author = random.choice(members)
            return author

        # title
        def generate_start_end(study):
            study_start, study_end = study.start, study.end
            result = random.choices(range(1, (study_end - study_start).days + 1), k=2)
            start = study_start + timedelta(min(result))
            end = study_start + timedelta(max(result))
            return start, end

        # sentence
        def generate_random_sentence():
            sentence = Faker(locale="en_US").sentence()
            return sentence

        # paragraph
        def generate_random_paragraph():
            paragraph = Faker(locale="en_US").paragraph()
            return paragraph

        # Create Task Objects
        studies = Study.objects.filter(is_active=True, status__lt=Study.Status.FINISHED)
        for study in studies:
            try:
                task_cnt = study.study_tasks.count()
                random_task_cnt = random.randint(2, 6)
                while task_cnt < random_task_cnt:
                    author = generate_random_author(study)
                    title = generate_random_sentence()
                    description = generate_random_paragraph()
                    start, end = generate_start_end(study)
                    created_at = datetime.combine(start, datetime.min.time())
                    updated_at = datetime.combine(end, datetime.min.time())
                    task, task_created = Task.objects.get_or_create(
                        study=study,
                        author=author,
                        title=title,
                        description=description,
                        start=start,
                        end=end,
                    )
                    if task_created:
                        task.created_at = created_at
                        task.updated_at = updated_at
                        task.save()
                        task_cnt += 1
                        created_task_cnt += 1
                        print(f"{created_task_cnt}개의 task가 생성되었습니다.")
            except:
                continue

        print(f"총 {created_task_cnt}개의 task 생성을 완료하였습니다.")
