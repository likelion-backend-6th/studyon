from django.urls import path

from . import views

app_name = "video"

urlpatterns = [
    path("<int:study_id>/", views.index, name="video_room"),
]
