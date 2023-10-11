from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/notice/", consumers.NoticeConsumer.as_asgi()),
]
