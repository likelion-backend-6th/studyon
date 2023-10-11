from channels.routing import URLRouter
from django.urls import path, re_path

import video.routing
import message.routing

websocket_urlpatterns = [
    path("", URLRouter(message.routing.websocket_urlpatterns)),
    path("video/", URLRouter(video.routing.websocket_urlpatterns)),
]
