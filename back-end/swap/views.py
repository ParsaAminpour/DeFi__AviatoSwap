from rich import print, pretty
from collections import deque
from queue import Queue
from django import forms
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.utils.translation import gettext as _
from .serializers import UserSerializer, walletSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
import django.contrib.auth.models as django_auth_models
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import status
from .forms import SignUp, login_form, UploadProfilePic, EditProfileForm
from django.views.generic.edit import UpdateView
from django.views.generic import DetailView, FormView, CreateView, ListView
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile, Wallet
from pathlib import Path
from django.contrib import messages
from datetime import datetime as dt 
from requests.auth import HTTPBasicAuth
from django.conf import settings
from asgiref.sync import sync_to_async, async_to_sync
import numpy as np
import asyncio, aiofiles
from rich.console import Console
console = Console()

class Home(View):
    def get(self, request):
        if request.user.is_anonymous:
            redirect('/login/')
        return render(request, 'home.html')

@async_to_sync
async def file_handler(file):
    async with aiofiles(f'{Path.cwd()}/swap/static/profiles{file.name}',\
        'wb+') as des:
        for chunk in file.chunks():
            await des.write(chunk) 

    path = Path(
        f'{Path.cwd()}/swap/static/profiles/{file.name}'
    )
    if  path.exists(): return True 
    else: return False



class EditProfile(UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'user_update.html'
    success_url = '/profile/'

    def get_object(self):
        return get_object_or_404(self.model, pk=self.request.user.id)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)



@csrf_exempt
@login_required(login_url='/login/')    
def Profile(request):
    if request.method == 'GET':
        form = UploadProfilePic()
        return render(request, 'profile.html' , {'form' : form})
    
    if request.method == 'POST':
        file_inserted = UploadProfilePic(
            data=request.POST, files=request.FILES
        )
        if file_inserted.is_valid():
            result = file_handler(request.FILES['file'])
            if result:
                request.user.profile_pic = file_inserted
                request.user.save()
                return redirect('/profile/')
            else:
                return render(
                    request, 'profile.html', {'error', 'Something went wrong'})
        return render(request, 'profile.html', {'error' : file_inserted.errors})

            
    
@csrf_exempt
def Signup(request):
    if request.method == 'GET':
        form = SignUp()
        return render(request, 'signup.html', {'form' : form})

    if request.method == 'POST':
        form = SignUp(request.POST)
        if form.is_valid(): 
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            form.save()


            new_user = authenticate(username=username, password=password)
            if new_user is not None:
                login(request, new_user)
            console.log(f'{username} was added')
            return redirect('/login/')
            # return render(request, 'profile.html', {
            #     'user' : request.user,
            # })
        return render(request, 'error.html', {'error' : form.errors})


@csrf_exempt
def Login(request):
    if request.method=='GET':
        form = login_form()
        return render(request, 'login.html', {'form' : form})
    
    if request.method == 'POST':
        form = login_form(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            result = authenticate(username=username, password=password)
            if result is not None:
                login(request, result)
                console.log('[bold green]username was logged in[/bold green]')
                return render(request, 'profile.html', {'user' : request.user})
            
            console.log('[bold red]authentication failed[/bold red]')
            return redirect('/login/')
        return redirect('/login/')


class Info(View):
    def get(self, request):
        return render(request, 'info.html', {})

class Swap(View):
    def get(self, request):
        return render(request, 'swap.html', {})
    
class ErrorPage(View):
    def get(self, request):
        return render(request, 'error.html', {'error' : ''})


### Serializers view ###
class AddUserApiView(APIView):
    permission_classes = (IsAuthenticated, )
    def post(self, request):
        user_serialize = UserSerializer(data=request.data)
        if user_serialize.is_valid():
            user_serialize.save()
            return Response(
                {'message' : f"{request.data.get('username')} added"},
                status=status.HTTP_201_CREATED)
        return Response({'message' : user_serialize.errors}, 
                        status=status.HTTP_406_NOT_ACCEPTABLE)




#sending data with requests module in python
@api_view(['GET','PUT'])
def user_api_view(request, user_id):
    if request.method == 'GET':
        user = get_object_or_404(User, id=user_id)
        user_serizlize = UserSerializer(instance=user)
        return Response({'message' : f'{user.username}'},
                        status=status.HTTP_200_OK)
    
    if request.method == 'PUT':
        user = get_object_or_404(User, id=user_id)
        user_serizlize_put = UserSerializer(
            instance=user,
            data=request.data,
            partial=True
        )
        if user_serizlize_put.is_valid():
            user_serizlize_put.save()
            return Response({'message' : f'{user.username}'},
                            status=status.HTTP_201_CREATED)

    return Response({'message' : 'BAD request method'},
                    status=status.HTTP_400_BAD_REQUEST)


class wallet_api_get(APIView):
    def get(self, request, wallet_id):
        wallet_ordered = get_object_or_404(Wallet, id=wallet_id)
        wallet_seri = walletSerializer(instance=wallet_ordered)
        return Response(wallet_seri.data)
    

class wallet_api_post(APIView):
    def post(self, request):
        wallet_serialize = walletSerializer(data=request.data)
        if wallet_serialize.is_valid():
            wallet_serialize.save()
            return Response(
                wallet_serialize.data,
                status=status.HTTP_201_CREATED
            )
        return Response(UserSerializer.errors,
                    status=status.HTTP_406_NOT_ACCEPTABLE)
