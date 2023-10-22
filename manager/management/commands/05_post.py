from datetime import datetime
import random

from django.core.management.base import BaseCommand

from faker import Faker

from manager.models import Post, Task, File


# TODO: 커맨드 활용
# https://docs.djangoproject.com/en/4.2/howto/custom-management-commands/#testing
class Command(BaseCommand):
    help = "PUSH Post DB"

    def handle(self, *args, **options):
        created_post_cnt = 0

        fileurl_list = [
            "https://kr.object.ncloudstorage.com/studyon/MEDIA/files/2023-09-30/002ebfb1-8db3-4791-a796-8b0235c79037.png",
            "https://kr.object.ncloudstorage.com/studyon/MEDIA/files/2023-09-30/0142a497-9865-403a-8358-27275ee7c0da.txt",
            "https://kr.object.ncloudstorage.com/studyon/MEDIA/files/2023-09-30/4622eee7-f61a-4493-b3a3-c00fa81ec95d.png",
            "https://kr.object.ncloudstorage.com/studyon/MEDIA/files/2023-10-18/6a3f2e03-156c-40e9-9551-5a69128e392b.pdf",
            "https://kr.object.ncloudstorage.com/studyon/MEDIA/files/2023-10-19/a39378f4-3aba-4b0e-9c8a-ca1da6d27de4.png",
        ]

        # file create
        for i, fileurl in enumerate(fileurl_list):
            exist_fileurl_list = File.objects.all().values_list("url", flat=True)
            if fileurl not in exist_fileurl_list:
                file, file_created = File.objects.get_or_create(
                    name=f"{i}번째 파일", url=fileurl
                )

        # author
        def get_random_author(task):
            members = task.study.members.all()
            author = random.choice(members)
            return author

        # sentence
        def generate_random_sentence():
            sentence = Faker(locale="en_US").sentence()
            return sentence

        # paragraph
        def generate_random_paragraph():
            paragraph = Faker(locale="en_US").paragraph()
            return paragraph

        # file
        def get_random_files():
            all_files = File.objects.all()
            file_cnt = random.randint(0, all_files.count() + 1)
            files = random.choices(all_files, k=file_cnt)
            return files

        # Create Post Objects
        tasks = Task.objects.filter(is_finished=False, is_active=True)
        print(tasks)
        for task in tasks:
            print(f"task:{task}")
            try:
                post_cnt = task.posts.count()
                random_post_cnt = random.randint(25, 50)
                while post_cnt < random_post_cnt:
                    title = generate_random_sentence()
                    author = get_random_author(task)
                    content = generate_random_paragraph()
                    files = get_random_files()
                    created_at = datetime.combine(task.start, datetime.min.time())
                    post, post_created = Post.objects.get_or_create(
                        title=title,
                        task=task,
                        author=author,
                        content=content,
                    )
                    if post_created:
                        if files:
                            post.files.add(*files)
                        post_cnt += 1
                        created_post_cnt += 1
                        print(f"{created_post_cnt}개의 post가 생성되었습니다.")
            except:
                continue

        print(f"총 {created_post_cnt}개의 post 생성을 완료하였습니다.")
