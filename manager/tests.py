from datetime import datetime
from django.template.response import TemplateResponse
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from unittest.mock import patch, MagicMock

from manager.models import File, Post, Study, Task

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

        cls.post01 = Post.objects.create(
            title="테스트 포스트01",
            task=cls.task01,
            author=cls.user01,
            content="테스트 게시글 본문01",
        )
        cls.post02 = Post.objects.create(
            title="테스트 포스트02",
            task=cls.task01,
            author=cls.user02,
            content="테스트 게시글 본문02",
        )
        cls.post03 = Post.objects.create(
            title="테스트 포스트03",
            task=cls.task01,
            author=cls.user03,
            content="테스트 게시글 본문03",
        )

        cls.file01 = File.objects.create(url="https://www.naver.com")

        cls.file02 = File.objects.create(url="https://www.google.com")

        cls.post01.files.add(cls.file01)
        cls.post01.files.add(cls.file02)

        cls.post_data = {
            "title": "새 게시글",
            "task_id": cls.task01.id,
            "author": cls.user01,
            "content": "새 게시글 작성 내용",
            "form-0-file": SimpleUploadedFile(
                "test.txt", b"Test File Data01", content_type="text/plain"
            ),
            "form-1-file": SimpleUploadedFile(
                "test.txt", b"Test File Data02", content_type="text/plain"
            ),
            "form-2-file": SimpleUploadedFile(
                "test.txt", b"Test File Data03", content_type="text/plain"
            ),
            "form-INITIAL_FORMS": 0,
            "form-TOTAL_FORMS": 3,
        }

        cls.modify_data = {
            "title": "수정 게시글",
            "content": "수정 게시글 작성 내용",
            "form-0-file": SimpleUploadedFile(
                "test.txt", b"Test File Data01", content_type="text/plain"
            ),
            "form-1-file": SimpleUploadedFile(
                "test.txt", b"Test File Data02", content_type="text/plain"
            ),
            "form-2-file": SimpleUploadedFile(
                "test.txt", b"Test File Data03", content_type="text/plain"
            ),
            "form-0-checkbox": "on",
            "form-INITIAL_FORMS": 0,
            "form-TOTAL_FORMS": 3,
        }

    def test_post_view(self):
        test_url = reverse("manager:post_list", args=[self.task01.pk])
        self.client.force_login(self.user01)

        res: TemplateResponse = self.client.get(test_url)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context_data["object_list"].count(), 3)

    def test_post_detail(self):
        test_url = reverse("manager:post_detail", args=[self.post01.pk])
        self.client.force_login(self.user01)

        res: TemplateResponse = self.client.get(test_url)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context_data["object"].title, self.post01.title)

    @patch("common.utils.client")
    def test_post_create(self, client: MagicMock):
        s3 = MagicMock()
        client.return_value = s3
        s3.upload_fileobj.return_value = None
        s3.put_object_acl.return_value = None

        test_url = reverse("manager:post_create", args=[self.task01.pk])
        self.client.force_login(self.user01)

        res: TemplateResponse = self.client.post(test_url, data=self.post_data)

        self.assertEqual(res.status_code, 302)
        self.assertEqual(Post.objects.count(), 4)
        self.assertEqual(File.objects.count(), 5)

        self.assertTrue(
            File.objects.last().url.startswith("https://kr.object.ncloudstorage.com")
        )

        self.assertEqual(s3.upload_fileobj.call_count, 3)
        self.assertEqual(s3.put_object_acl.call_count, 3)

    @patch("common.utils.client")
    def test_post_update(self, client: MagicMock):
        s3 = MagicMock()
        client.return_value = s3
        s3.upload_fileobj.return_value = None
        s3.put_object_acl.return_value = None

        test_url = reverse("manager:post_modify", args=[self.post01.pk])
        self.client.force_login(self.user01)

        res: TemplateResponse = self.client.post(test_url, data=self.modify_data)

        self.assertEqual(res.status_code, 302)
        self.assertEqual(Post.objects.first().title, self.modify_data.get("title"))
        self.assertEqual(File.objects.count(), 4)

        self.assertTrue(
            File.objects.last().url.startswith("https://kr.object.ncloudstorage.com")
        )

        self.assertEqual(s3.upload_fileobj.call_count, 3)
        self.assertEqual(s3.put_object_acl.call_count, 3)

    def test_post_delete(self):
        test_url = reverse("manager:post_delete", args=[self.post01.pk])
        self.client.force_login(self.user01)

        res: TemplateResponse = self.client.post(test_url)

        self.assertEqual(res.status_code, 204)
        self.assertEqual(Post.objects.count(), 2)
        with self.assertRaises(Post.DoesNotExist):
            Post.objects.get(id=self.post01.pk)
