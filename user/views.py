from typing import Any

from django.contrib import auth
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import ListView, View

from .models import Profile, Review


def logout(request):
    auth.logout(request)
    return redirect("recruits:index")


class LoginView(View):
    template_name = "users/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("recruits:index")
        form = AuthenticationForm(request=request)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)
            return redirect("recruits:index")

        return render(request, self.template_name, {"form": form})


class SignupView(View):
    template_name = "users/signup.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST["username"]
        nickname = request.POST["nickname"]
        password = request.POST["password"]
        password_check = request.POST["password_check"]
        if User.objects.filter(username=username).exists():
            return render(
                request, self.template_name, {"error": "username is already exists"}
            )
        if Profile.objects.filter(nickname=nickname).exists():
            return render(
                request, self.template_name, {"error": "nickname is already exists"}
            )
        if password == password_check:
            user = User.objects.create_user(username=username, password=password)
            Profile.objects.create(user=user, nickname=nickname)
            return redirect("users:login")
        else:
            return render(
                request,
                self.template_name,
                {"error": "password and password_check is not same"},
            )


class MyHistoryView(ListView):
    model = Review
    template_name = "users/info.html"
    context_object_name = "reviews"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["my_reviews"] = Review.objects.filter(reviewer=self.request.user)
        return context

    def get_queryset(self):
        user = self.request.user
        return super().get_queryset().filter(reviewee=user)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            return super().get(request, *args, **kwargs)
        return redirect("users:login")


class UserSocialSignupView(View):
    def get(self, request):
        profile = Profile.objects.filter(user=request.user)
        if not profile:
            return render(request, "users/social_signup.html")
        else:
            return redirect("recruits:index")

    def post(self, request):
        nickname = request.POST["nickname"]
        if Profile.objects.filter(nickname=nickname).exists():
            return render(
                request,
                "users/social_signup.html",
                {"error": "nickname is already exists"},
            )
        else:
            user = request.user
            Profile.objects.create(user=request.user, nickname=nickname)
            return redirect("users:social_signup")
