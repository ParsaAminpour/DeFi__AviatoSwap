from django.urls import re_path
from . import consumer

websocket_urlpatterns = [
	re_path(r'ws/chat/?P<room_name>/$', consumer.ChatRoomConsumer.as_asgi())
]