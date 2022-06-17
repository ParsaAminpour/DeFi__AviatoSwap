from rich import print, pretty
from collections import deque
from queue import Queue
from django import forms
from django.http import HttpResponseRedirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, DjangoUnicodeDecodeError, force_str # as force_text in Django v4.0
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from .utils import gen_token
from django.contrib.auth import get_user_model

from django.utils.translation import gettext as _
from .serializers import UserSerializer, walletSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
import django.contrib.auth.models as django_auth_models
from rest_framework.views import APIView
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
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
from random import randint
from hashlib import sha256
from requests.auth import HTTPBasicAuth
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

            

@require_http_methods(['GET','POST'])
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
            user = form.save(commit=False)
            user.is_active = False
            # user.save()

            current_site = get_current_site(request)

            email_message = EmailMessage(
                'Registration Validation',
                render_to_string('email_template.html', {
                        'user' : user,
                        'domain' : current_site.domain,
                        'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                        'token' : gen_token.make_token(user)    
                    }),
                settings.EMAIL_HOST_USER,
                [form.cleaned_data.get('email')])
            email_message.send()

            messages.add_message(request, messages.SUCCESS, 'account created successfuly')

        return render(request, 'error.html', {'error' : form.errors})


class ActivateView(View):
    def get(self, request, uidb64, token):
        User = get_user_model()
        try:
            uid_decoded = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid_decoded)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and gen_token.check_token(user, token):
            user.is_active = True
            user.save()

            # new_user = authenticate(username=username, password=password)
            # if new_user is not None:
            #     login(request, new_user)

            console.log(f'[bold green]{user.username} was added[/bold green]')
            messages.add_message(request, messages.INFO, f'{user.username} registered')
            return redirect('login')

        msg = f'[bold red]An error occured in {self.__class__.__name__}[/bold red]'
        console.log(f'[bold red]{msg}[/bold red]')
        return render(request, 'error.html', {'error' : msg}, status=401)


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
                console.log(f'[bold green]{username} was logged in[/bold green]')
                return render(request, 'profile.html', {'user' : request.user})
            
            console.log('[bold red]authentication failed[/bold red]')
            return redirect('/login/')
        return redirect('/login/')


class Info(View):
    def get(self, request):
        return render(request, 'info.html', {})

class Swap(View):
    def get(self, request):
        return render(request, 'trading.html', {})
    
class ErrorPage(View):
    def get(self, request):
        return render(request, 'error.html', {'error' : ''})

class Donation(View):
    def get(self, request):
        return render(request, 'donation.html', {})


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
    
    def put(self, request, wallet_id):
        wallet_ordered = get_object_or_404(Wallet, id=wallet_id)
        wallet_seri = walletSerializer(
            instance=wallet_ordered,
            data = request.data,
            partial=True)
        if wallet_seri.is_valid():
            wallet_seri.save()
            # console.log(
                # f'[bold yellow]{wallet_ordered.address} was changed to {request.data.address}[/bold yellow]')
            return Response(wallet_seri.data,
                status=status.HTTP_201_CREATED)
        return Response(wallet_seri.errors,
            status=status.HTTP_406_NOT_ACCEPTABLE)



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
