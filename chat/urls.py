from django.urls import path

from chat import views

app_name = "chat"

urlpatterns = [
    path("room/<int:study_id>/", views.study_chat, name="study_chat_room"),
]
