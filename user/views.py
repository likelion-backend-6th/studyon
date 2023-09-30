from typing import Any
from django.db import models
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View, ListView
from django.contrib.auth.models import User
from django.contrib import auth

from .models import Review


def logout(request):
    auth.logout(request)
    return redirect("recruits:index")


class LoginView(View):
    template_name = "users/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("recruits:index")
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST["username"]
        password = request.POST["password"]
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect("recruits:index")
        else:
            return render(
                request,
                self.template_name,
                {"error": "username or password is incorrect"},
            )


class SignupView(View):
    template_name = "users/signup.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST["username"]
        password = request.POST["password"]
        password_check = request.POST["password_check"]
        if User.objects.filter(username=username).exists():
            return render(
                request, self.template_name, {"error": "username is already exists"}
            )
        if password == password_check:
            User.objects.create_user(username=username, password=password)
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
        print(context)
        return context

    def get_queryset(self):
        user = self.request.user
        return super().get_queryset().filter(reviewee=user)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            return super().get(request, *args, **kwargs)
        return redirect("users:login")
