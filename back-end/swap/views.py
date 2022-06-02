from functools import partial
from rich import print, pretty
from pyexpat import model
from xmlrpc.client import ResponseError
from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
import numpy as np
from platformdirs import user_state_dir
from pydantic import UrlSchemeError
from yaml import serialize
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import status
from .forms import SignUp, login_form
from django.views.generic import DetailView, FormView, CreateView, ListView
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile
from django.contrib import messages
from datetime import datetime 
from requests.auth import HTTPBasicAuth
import numpy as np
from rich.console import Console
console = Console()

class Home(View):
    def get(self, request):
        return render(request, 'home.html')

@login_required(login_url='/login/')
def Profile(request):
    if request.method == 'GET':
        return render(request, 'profile.html' , {})

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

            # relevant_profile = Profile.objects.get(username=username)

            new_user = authenticate(username=username, password=password)
            if new_user is not None:
                login(request, new_user)
            console.log(f'{username} was added')
            return redirect('/login/')
            # return render(request, 'profile.html', {
            #     'user' : request.user,
            # })
        return render(request, 'error.html', {'error' : form.errors})


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
            else:
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



@api_view(['GET'])
def testPage(request):
    if request.method == 'GET':
        return Response({'message' : 'This is test'}, status=status.HTTP_200_OK)
    return Response({'message' : 'error'})