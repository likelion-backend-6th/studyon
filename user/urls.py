from django.urls import path
from user import views

app_name = "users"
urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("logout/", views.logout, name="logout"),
    path("info/", views.MyHistoryView.as_view(), name="info"),
    path("social_signup/", views.UserSocialSignupView.as_view(), name="social_signup"),
]
