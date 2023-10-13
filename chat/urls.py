from django.urls import path

from chat import views

app_name = "chat"

urlpatterns = [
    path("room/<int:study_id>/create/", views.make_chat_room, name="make_chat_room"),
    # path("room/<int:room_id>/chat/", views.chat_room, name="chat_room"),
    path("room/<int:room_id>/chat/", views.ChatRoomView.as_view(), name="chat_room"),
]
