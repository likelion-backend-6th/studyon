from django.urls import path

from chat import views

app_name = "chat"

urlpatterns = [
    path("room/<int:study_id>/", views.make_chat_room, name="make_chat_room"),
    path("room/<int:study_id>/<int:tag_id>/", views.chat_room, name="chat_room"),
    path("room/<int:study_id>/tags/", views.room_tag_list, name="room_tag_list"),
]
