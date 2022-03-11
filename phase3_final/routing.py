from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from django.urls import path
from phase3 import consumers

ws_pattern = [
    path('ws/<int:id>', consumers.EventConsumer.as_asgi()),
]

application = ProtocolTypeRouter(
    {"http": get_asgi_application(),
     'websocket': AuthMiddlewareStack(URLRouter(ws_pattern))
     }
)
