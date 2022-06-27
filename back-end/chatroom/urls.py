from django.urls import path
from .views import ChatList, RoomView, get_message_api, add_message_api
from graphene_django.views import GraphQLView
from .schema import schema

urlpatterns = [
	path('rooms/', ChatList.as_view(), name='rooms'),	
	path('rooms/<int:room_id>/', RoomView.as_view(), name='room'),
	path('api/<int:msg_id>/', get_message_api.as_view(), name='api_view'),
	path('api/message/add/', add_message_api.as_view(), name='add_msg_api'),
	path('graphql/', GraphQLView.as_view(graphiql=True, schema=schema))
]	