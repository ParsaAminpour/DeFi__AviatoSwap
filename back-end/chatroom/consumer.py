#consumers are akin to django
import async_timeout
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import sync_to_async, async_to_sync
from cryptography.fernet import Fernet
from zmq import SOCKS_PASSWORD
from .models import Room, Message
from .crypto import Crypto
import json


class ChatConsumer(WebsocketConsumer):
	def __init__(self, *args, **kwargs):
		super().__init__(args, kwargs)
		self.room_name = None
		self.room_group_name = None
		self.room = None

	def connect(self):
		self.room_name = self.scope['url_route']['kwargs']['room_name']
		self.room_group_name = f'chat_{self.room_name}'
		self.room = Room.objects.get(name=self.room_name)
		
		self.accept()
		async_to_sync(self.channel_layer.group_add)(
			self.room_group_name,
			self.channel_name)


	def disconnect(self, close_code):
		async_to_sync(self.channel_layer.group_discard)(
			self.room_group_name,
			self.channel_name
		)		

	def receive(self, text_data=None, bytes_data=None):
		data = json.loads(text_data).get("message")

		async_to_sync(self.channel_layer.group_send)(
			self.room_group_name,
			{
				'type' : 'msg_handler',
				'message' : data
			}
		)

	def msg_handler(self, event):
		self.send(text_data=json.dumps(event))