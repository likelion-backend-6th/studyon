from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.models import User
from django.contrib import auth


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


def logout(request):
    auth.logout(request)
    return redirect("recruits:index")
