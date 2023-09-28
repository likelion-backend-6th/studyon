from django.urls import path

from recruit import views


app_name = "recruits"

urlpatterns = [
    path("", views.RecruitView.as_view(), name="index"),
    path("recruit/<int:pk>/like/", views.like_recruit, name="like_recruit"),
    path("recruit/<int:pk>/unlike/", views.unlike_recruit, name="unlike_recruit"),
]
