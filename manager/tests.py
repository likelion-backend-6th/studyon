from datetime import datetime
from django.template.response import TemplateResponse
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from manager.models import Post, Study, Task

from recruit.models import Recruit


class PostTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user01 = User.objects.create_user(username="user01", password="1234")
        cls.user02 = User.objects.create_user(username="user02", password="1234")
        cls.user03 = User.objects.create_user(username="user03", password="1234")

        cls.study = Study.objects.create(
            creator=cls.user01,
            title="테스트 모집공고",
            start=datetime(2023, 9, 1),
            end=datetime(2023, 10, 31),
            process="테스트 프로세스",
            info="테스트 인포",
            status=Study.Status.IN_PROGRESS,
        )
        cls.study.members.add(cls.user02, cls.user03)

        cls.recruit = Recruit.objects.create(
            study=cls.study,
            creator=cls.user01,
            title="테스트 모집공고",
            deadline=datetime(2023, 8, 31),
            start=datetime(2023, 9, 1),
            end=datetime(2023, 10, 31),
            total_seats=4,
            target="테스트 타겟",
            process="테스트 프로세스",
            info="테스트 인포",
        )
        cls.recruit.members.add(cls.user02, cls.user03)

        cls.task01 = Task.objects.create(
            study=cls.study,
            author=cls.user01,
            title="테스트 태스크01",
            description="테스트 설명",
            start=datetime(2023, 9, 1),
            end=datetime(2023, 9, 10),
            is_finished=True,
        )
        cls.task02 = Task.objects.create(
            study=cls.study,
            author=cls.user01,
            title="테스트 태스크02",
            description="테스트 설명",
            start=datetime(2023, 9, 11),
            end=datetime(2023, 9, 30),
            is_finished=True,
        )
        cls.task03 = Task.objects.create(
            study=cls.study,
            author=cls.user01,
            title="테스트 태스크02",
            description="테스트 설명",
            start=datetime(2023, 10, 1),
            end=datetime(2023, 10, 31),
        )

        cls.post = Post.objects.create(
            title="테스트 포스트01",
            task=cls.task01,
            author=cls.user01,
            content="테스트 게시글 본문01",
        )
        cls.post = Post.objects.create(
            title="테스트 포스트02",
            task=cls.task01,
            author=cls.user02,
            content="테스트 게시글 본문02",
        )
        cls.post = Post.objects.create(
            title="테스트 포스트03",
            task=cls.task01,
            author=cls.user03,
            content="테스트 게시글 본문03",
        )

    def test_post_view(self):
        test_url = reverse("manager:post_list", args=[self.task01.pk])
        client = Client()
        client.force_login(self.user01)

        res: TemplateResponse = client.get(test_url)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context_data["object_list"].count(), 3)
