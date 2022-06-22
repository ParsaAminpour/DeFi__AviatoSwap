from django.shortcuts import render
from django.views import View
from .models import Room, Message 
from django.shortcuts import get_object_or_404


class ChatList(View):
	def get(self, request):
		rooms = Room.objects.all()
		return render(request, 'index.html', {'rooms':rooms})

class RoomView(View):
	def get(self, request, room_id):
		room = get_object_or_404(Room,  id=room_id)
		messages = Message.objects.values_list('message', flat=True)
		pass
