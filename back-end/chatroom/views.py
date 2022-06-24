from django.shortcuts import render
from django.views import View
from .models import Room, Message 
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import MessageSerialize

class ChatList(View):
	def get(self, request): 
		rooms = Room.objects.all()
		return render(request, 'index.html', {'rooms':rooms})


class RoomView(View):
	def get(self, request, room_id):
		room = get_object_or_404(Room,  id=room_id)

		if 'recently_view' not in request.session:
			request.session['recently_view'] = [room_id]  

		elif room_id in list(request.session.get('recently_view')):
			request.session.get('recently_view').remove(room_id)
			# re-adding to top of the list 
			request.session['recently_view'].insert(0,room_id)

		else:
			request.session['recently_view'].insert(0, room_id)
			
		result = Room.objects.filter(
			id__in=request.session.get('recently_view'))

		context = {
			'room' : room,
			'messages' : room.message.all(),
			'recently' : result
		}
		return render(request, 'room.html', context=context)


class get_message_api(APIView):
	def get(self, request, msg_id):
		message = get_object_or_404(Message, id=msg_id)
		msg_seri = MessageSerialize(instance=message)

		if msg_seri.is_valid():
			return Response(
				msg_seri.data(),
				status=status.HTTP_200_OK)
		return Response(
			msg_seri.errors,
			status=status.HTTP_406_NOT_ACCEPTABLE)


class add_message_api(APIView):
	def post(self, request):
		msg_seri = MessageSerialize(data=request.data)
		if msg_seri.is_valid():
			msg_seri.save()
			return Response(
				'Created successfully',
				status=status.HTTP_201_CREATED)

		return Response(msg_seri.errors, status=status.HTTP_406_NOT_ACCEPTABLE)
