from django.urls import path

from . import consumers

websoket_urlpatterns = [
    path("ws/notice/", consumers.NoticeConsumer.as_asgi()),
]
