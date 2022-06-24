from rich import print, pretty
from collections import deque
from queue import Queue
from django import forms
from django.http import HttpResponseRedirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic.detail import SingleObjectMixin

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, DjangoUnicodeDecodeError, force_str # as force_text in Django v4.0
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from .utils import gen_token
from django.contrib.auth import get_user_model
from django.http.response import HttpResponseForbidden

from django.urls import reverse
from django.shortcuts import reverse as rev

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth import models
from django.contrib.auth.models import User, Group, Permission

from django.core.management.utils import get_random_secret_key
from django.core.signing import TimestampSigner
# from django.core.signing import BadSigning

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
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects 

from asgiref.sync import sync_to_async, async_to_sync
import asyncio, aiofiles, aiohttp # tsak:finding its exception handler of aiohttp
import requests
import numpy as np
from rich.console import Console
import stripe #for payment

strip_api_key = settings.STRIPE_API_KEY
console = Console()


class Home(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            redirect('/login/')
        return render(request, 'home.html')


@async_to_sync
async def file_handler(file):
    async with aiofiles(f'{settings.BASE_DIR}/media',\
        'wb+') as des:
        for chunk in file.chunks():
            await des.write(chunk) 

    path = Path(
        f'{Path.cwd()}/swap/static/profiles/{file.name}'
    )
    if  path.exists(): return True  
    else: return False


# for working with APIs
async def fetching(session, url:str):
    try:    
        async with session.get(url) as response:
            assert response.status == 200
            data = response.jsno()
            return data
    except Exception as err:
        return response.reason


@async_to_sync
async def get_api(url:str):
    actions = []
    async with aiohttp.ClientSession() as session:
        actions.append(
            asyncio.ensure_future(fetching(session, url)))

    result = [*asyncio.gather(*actions)]
    return result


class CustomePermission(PermissionRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect_to_login(self.request.get_full_path(),
                self.get_login_url(), self.get_redirect_field_name())

        if not self.has_permission():
            return HttpResponseForbidden(self.permission_denied_message)
        
        return super(CustomePermission, self).dispatch(request, *args, **kwargs)


class EditProfile(CustomePermission, UpdateView):
    permission_denied_message = '403 Forbidden<br /><center><h2>This page is forbidden for you</h2></center>'
    login_url='/login/'
    redirect_field_name = 'next'
    reaise_exception = True
    permission_required = 'user.change_user'
    model = User
    form_class = EditProfileForm
    template_name = 'user_update.html'
    success_url = '/profile/'


    def get_object(self):
        return get_object_or_404(self.model, pk=self.request.user.id)

    def post(self, request, *args, **kwargs):
        user = request.user
        file = request.FILES.get('profile_pic')
        if file is not None:
            user.profile_pic = file
            user.save()
        # messages.SUCCESS(request, 'profile has been changed')
        return super().post(request, *args, **kwargs)


@csrf_exempt
@login_required(login_url='/login/')    
def Profile(request):
    if request.method == 'GET':
        if 'login' in list(get_current_site(request).domain.split('/')):
            redirect('profile')

        form = UploadProfilePic()
        return render(request, 'profile.html' , {'user' : request.user})
    
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

# api security 


@require_http_methods(['GET','POST'])
@csrf_exempt
def Signup(request):
    if request.method == 'GET':
        form = SignUp()
        return render(request, 'signup.html', {'form' : form})

    if request.method == 'POST':
        form = SignUp(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            authenticate(username=user.username, password=user.password)

            return redirect('login')
            # return render(request, 'profile.html', {'user':user})
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
            _ = User.objects.get(username=form.cleaned_data.get('username'))
            if not _.is_active:
                return HttpResponseForbidden(
                f'<center><h1><i>Firstoff please activate your accuont via email verification link</i></h1></center>')

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            result = authenticate(username=username, password=password)
            if result is not None:
                login(request, result)
                console.log(f'[bold green]{username} was logged in[/bold green]')
                return render(request, 'home.html', {})
            
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

class Chatroom(View):
    def get(self, request):
        pass

    def post(self, request, msg_id):
        pass

    def delete(self, request, msg_id):
        pass

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


#class MessagesApi(APIView):
 #   permission_classes = ()
  #  def get(self, request):
  #      if request.user.is_staff:
#         return Response(
 #                   {'message' : 'This page is forbidden for you'},
  #                  status=status.HTTP_403_FORBIDDEN)
   # pass

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
