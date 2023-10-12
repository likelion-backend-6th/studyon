from django.urls import re_path

from chat import consumers

websocket_urlpatterns = [
    re_path(
        r"ws/chat/room/(?P<study_id>\w+)/(?P<tags>.+)/$",
        consumers.ChatConsumer.as_asgi(),
    ),
]
