from django.shortcuts import render
from django.views import View
from .models import Room, Message 
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from textblob import TextBlob
from .serializers import MessageSerialize
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from rich import print, pretty
from django.conf import settings
import os, json
import aiohttp, asyncio
from asgiref.sync import sync_to_async, async_to_sync
import tweepy


class ChatList(LoginRequiredMixin, View):
	def get(self, request):
		API_KEY = settings.API_KEY
		API_SECRET_KEY = settings.API_SECRET_KEY
		BEARER = settings.BEARER
		ACCESS_TOKEN = settings.ACCESS_TOKEN
		ACCESS_TOKEN_SECRET = settings.ACCESS_SECRET_TOKEN

		client = tweepy.Client(bearer_token = BEARER)

		q ="#BTC OR #ETH"
		response2 = asyncio.gather(client.search_recent_tweets(query=q, user_fields=['profile_image_url', 'username'], 
			expansions=["author_id","referenced_tweets.id"], max_results=10))

		result = {data.author_id : data.text.strip() for data in response2.data}
		users = [client.get_user(id=key) for key in list(result.keys())]
		usernames = [user.data.username for user in users]
		
		tweets = list(result.values())

		tweet_ids = [data.referenced_tweets for data in response2.data]
		urls = []
		for username, id_ in zip(usernames, tweet_ids):
			urls.append(
				f"https://twitter.com/{username}/status/{id_}")

		main_result = zip(usernames,tweets,urls)
		rooms = Room.objects.all()	

		ctx = {'rooms' : rooms, 'tweets' : main_result}
		return render(request,'index.html', context=ctx)




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
