from base64 import decode
from http import cookies
from django.http import HttpResponseServerError
from django.shortcuts import redirect, render
from django.core.exceptions import PermissionDenied
from django.views import View
from graphene import resolve_only_args
from graphql import is_valid_literal_value
from jwt import DecodeError
from .models import Room, Message 
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from .forms import Chat
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from textblob import TextBlob
from .serializers import MessageSerialize
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import resolve
from rich import print, pretty
from django.conf import settings
import redis
import channels.layers
import os, json
import aiohttp, asyncio
from rich import print, pretty
from rich.console import Console
from rich.traceback import Trace
from asgiref.sync import sync_to_async, async_to_sync
import tweepy
console = Console()	

class ChatList(LoginRequiredMixin, View):
	def get(self, request):
		API_KEY = settings.API_KEY
		API_SECRET_KEY = settings.API_SECRET_KEY
		BEARER = settings.BEARER
		ACCESS_TOKEN = settings.ACCESS_TOKEN
		ACCESS_TOKEN_SECRET = settings.ACCESS_SECRET_TOKEN

		rooms = Room.objects.all()	

		ctx = {'rooms' : rooms}
		return render(request,'index.html', context=ctx)


def get_data_from_twitter():
		'''
			Unfortunately my twitter API has been crashed to some problem
			I'll fix it ASAP
		'''
		client = tweepy.Client(bearer_token = BEARER)

		q ="#BTC OR #ETH"
		response2 = client.search_recent_tweets(query=q, user_fields=['profile_image_url', 'username'], 
			expansions=["author_id","referenced_tweets.id"], max_results=10)

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

class RoomView(View):
	def __init__(self):
		try:
			self.r = redis.Redis(
				"localhost", port=6379, db=0, decode_responses=True)
		except Exception:
			return HttpResponseServerError("Redis has some problem")

	def get(self, request, room_id:int):
		room = get_object_or_404(Room,  id=room_id)
		form = Chat()

		for msg in self.r.lrange(f'{room.name}_messages',0,-1):
			console.log(f"[blue]{msg}[/blue]")

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
			'messages' : list(reversed(self.r.lrange(f"{room.name}_messages",0,-1))),
			'recently' : result,
			'form' : form
		}
		return render(request, 'room.html', context=context)


	def post(self, request):
		id_ = request.get_full_path().split('/')[3]
		room = get_object_or_404(Room, id=id_)

		form = Chat(request.POST)

		if form.is_valid():
			if len(self.r.keys()) == 0 and len(Message.objects.all()) != 0:  
				console.log("cloning from db into redis...")
				for message in Message.objects.all():
					self.r.lpush(f'{room.name}_messages', message)

			msg = form.save(commit=False)
			room.message.add(msg)
			# owner = msg.owner
			self.r.lpush(f"{room.name}_messages", msg.message)	

			room.save()
			return redirect(f"/chat/room/{room.id}/cdscsd")

		return PermissionDenied("You can NOT send message as much as 256 or empty")


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
