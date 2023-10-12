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

import chat.routing
import message.routing
import video.routing

ENV = os.getenv("RUN_MODE", "base")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"config.settings.{ENV}")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                video.routing.websocket_urlpatterns
                + message.routing.websocket_urlpatterns
                + chat.routing.websocket_urlpatterns
            )
        ),
    }
)