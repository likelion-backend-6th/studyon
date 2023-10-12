"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path

import chat.consumers
import message.consumers
import video.consumers

ENV = os.getenv("RUN_MODE", "base")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"config.settings.{ENV}")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    path("ws/notice/", message.consumers.NoticeConsumer.as_asgi()),
                    path(
                        "ws/video/<int:study_id>/",
                        video.consumers.VideoConsumer.as_asgi(),
                    ),
                    path(
                        "ws/chat/room/<str:room_id>/",
                        chat.consumers.ChatConsumer.as_asgi(),
                    ),
                ]
            )
        ),
    }
)
