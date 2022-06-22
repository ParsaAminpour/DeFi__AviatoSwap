from django.urls import path
from .views import ChatList

urlpatterns = [
	path('rooms/', ChatList.as_view(), name='rooms'),	
]