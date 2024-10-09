from django.urls import path
from .consumers import *

# Define WebSocket URL patterns for chatroom consumers.
websocket_urlpatterns = [
    path("ws/chatroom/<chatroom_name>", ChatroomConsumer.as_asgi()),
]