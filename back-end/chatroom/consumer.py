from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async, async_to_sync
from cryptography.fernet import Fernet
from .models import Room, Message
from .crypto import Crypto
import json


class ChatRoomConsumer(AsyncWebsocketConsumer):
	def __init__(self):
		self.room_name = None
		self.room_group_name = None
		self.room = None
		self.message = None
		self.user = None
		self.crypto = Crypto()

	@async_to_sync
	async def connect(self):
		self.room_name = self.scope['url_route']['kwargs']['room_name']
		self.room_group_name = f'group_{room_name}'
		self.user = scope['user']

		await self.accept()

		await self.channel_layer.add_group(
			self.room_group_name,
			self.channel_name)

		self.room = Room.objects.get(name=room_group_name)
		self.room.add_to_group(self.user)


	@async_to_sync
	async def disconnect(self, room_code):
		await self.channel_layer.group_discard(
			self.room_group_name,
			self.channel_name)

		self.room.remove_from_group(self.user)


	@async_to_sync
	async def receive(self, text_data):
		if self.user.is_authenticated:
			data = json.loads(text_data)
			message = data.get('message')
			username = self.user.username

			await self.channel_layer.group_send(
				room_group_name,{
					'type' : 'message_handler',
					'message' : message,
					'username' : username
				})

			msg = Message.objects.create(message=message, owner=self.user)
			self.room.add_message_to_room(msg)

	#generating key for consumer section 

	@async_to_sync
	async def message_handler(self, event):
		message = event.get('message')
		username = event.get('username')
		# assert username != None

		self.send(text_data=json.dumps({
			'username' : username,
			'message' : message
			}))


