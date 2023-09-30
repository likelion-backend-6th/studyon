from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class PostTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.base_user = User.objects.create_user(
            username="base_user", password="base_user"
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
                "password": "base_user",
                "password_check": "base_user",
            },
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("exists", res.context["error"])

    def test_user_logout(self):
        self.client.login(username="base_user", password="base_user")
        res = self.client.get(reverse("users:logout"))
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse("recruits:index"))
