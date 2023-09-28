from django.urls import path

from . import views


app_name = "manager"

urlpatterns = [
    path("", views.StudyView.as_view(), name="stuydies_list"),
    path("<int:pk>/", views.StudyDetailView.as_view(), name="stuydy_detail"),
    path("tasks/<int:pk>/", views.PostView.as_view(), name="post_list"),
]
