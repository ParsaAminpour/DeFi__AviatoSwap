from django.urls import path
from .views import ChatList, RoomView

urlpatterns = [
	path('rooms/', ChatList.as_view(), name='rooms'),	
	path('rooms/<int:room_id>/', RoomView.as_view(), name='room')
]