from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Review, Profile
from manager.models import Study


class UserTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.base_user = User.objects.create_user(
            username="base_user", password="base_user"
        )
        cls.base_profile = Profile.objects.create(
            user=cls.base_user, nickname="BaseUser"
        )

        cls.user1 = User.objects.create_user(
            username="study_user1", password="study_user1"
        )
        cls.user2 = User.objects.create_user(
            username="study_user2", password="study_user2"
        )
        cls.study = Study.objects.create(
            creator=cls.user1,
            title="test_study",
            start="2021-01-01",
            end="2021-01-01",
            process="test",
            info="test",
        )
        cls.study.members.add(cls.user1)
        cls.study.members.add(cls.user2)
        for i in range(3):
            user = User.objects.create_user(username=f"user{i}", password=f"user{i}")
            Review.objects.create(
                study=cls.study,
                reviewer=cls.base_user,
                reviewee=user,
                score=i,
                review="good",
            )
            Review.objects.create(
                study=cls.study,
                reviewer=user,
                reviewee=cls.base_user,
                score=i,
                review="good",
            )

    def test_login_page(self):
        res = self.client.get(reverse("users:login"))
        self.assertEqual(res.status_code, 200)

    def test_user_login(self):
        res = self.client.post(
            reverse("users:login"), {"username": "base_user", "password": "base_user"}
        )
        self.assertEqual(res.status_code, 302)

    def test_user_bad_login(self):
        res = self.client.post(
            reverse("users:login"),
            {"username": "base_user", "password": "bad_password"},
        )
        # 다시 로그인 페이지로 돌아가는지 확인
        self.assertEqual(res.status_code, 200)

    def test_user_signup_page(self):
        res = self.client.get(reverse("users:signup"))
        self.assertEqual(res.status_code, 200)

    def test_user_signup(self):
        res = self.client.post(
            reverse("users:signup"),
            {
                "username": "new_user",
                "nickname": "new_user",
                "password": "new_user",
                "password_check": "new_user",
            },
        )
        self.assertEqual(res.status_code, 302)
        user = User.objects.filter(username="new_user").first()
        self.assertIsNotNone(user)

    def test_user_bad_signup(self):
        res = self.client.post(
            reverse("users:signup"),
            {
                "username": "new_user",
                "nickname": "new_user",
                "password": "new_user",
                "password_check": "bad_password",
            },
        )
        self.assertEqual(res.status_code, 200)
        user = User.objects.filter(username="new_user").first()
        self.assertIsNone(user)

        # 유저 중복
        res = self.client.post(
            reverse("users:signup"),
            {
                "username": "base_user",
                "nickname": "base_user",
                "password": "base_user",
                "password_check": "base_user",
            },
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("존재", str(res.context["form"].errors))

    def test_user_logout(self):
        self.client.login(username="base_user", password="base_user")
        res = self.client.get(reverse("users:logout"))
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse("recruits:index"))

    def test_user_info_with_no_user(self):
        res = self.client.get(reverse("users:info"))
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse("users:login"))

    def test_user_info(self):
        self.client.login(username="base_user", password="base_user")
        res = self.client.get(reverse("users:info"))
        self.assertEqual(res.status_code, 200)

    def test_write_review(self):
        review_data = {
            "review": "good",
            "score": 5,
            "study": self.study.id,
        }
        self.client.force_login(self.user1)
        res = self.client.post(
            reverse("users:write_review", args=[self.user2.id]), review_data
        )
        review = Review.objects.get(reviewer=self.user1, reviewee=self.user2)
        print(review)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse("manager:study_detail", args=[self.study.id]))
        self.assertEqual(review.score, 5)
        self.assertEqual(review.review, "good")

    def test_write_review_update(self):
        Review.objects.create(
            study=self.study,
            reviewer=self.user1,
            reviewee=self.user2,
            score=5,
            review="good",
        )
        review_data = {
            "review": "verry good",
            "score": 3,
            "study": self.study.id,
        }
        self.client.force_login(self.user1)
        res = self.client.post(
            reverse("users:write_review", args=[self.user2.id]), review_data
        )
        review = Review.objects.get(reviewer=self.user1, reviewee=self.user2)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse("manager:study_detail", args=[self.study.id]))
        self.assertEqual(review.score, 3)
        self.assertEqual(review.review, "verry good")

    def test_write_review_same_user(self):
        review_data = {
            "review": "good",
            "score": 5,
            "study": self.study.id,
        }
        self.client.force_login(self.user1)
        res = self.client.post(
            reverse("users:write_review", args=[self.user1.id]), review_data
        )
        self.assertEqual(res.status_code, 404)

    def test_write_review_bad_user(self):
        review_data = {
            "score": 5,
            "review": "good",
            "study": self.study.id,
        }
        self.client.force_login(self.user1)
        res = self.client.post(
            reverse("users:write_review", args=[self.base_user.id]), review_data
        )
        self.assertEqual(res.status_code, 404)
