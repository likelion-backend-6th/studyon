from django.urls import path

from . import views


app_name = "manager"

urlpatterns = [
    path("", views.StudyView.as_view(), name="studies_list"),
    path("<int:pk>/", views.StudyDetailView.as_view(), name="study_detail"),
    path("<int:pk>/done", views.StudyDoneView.as_view(), name="study_done"),
    path("<int:pk>/finished", views.StudyDoneView.as_view(), name="study_finished"),
    path("tasks/<int:pk>/", views.PostView.as_view(), name="post_list"),
]
