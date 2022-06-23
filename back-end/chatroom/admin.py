from django.contrib import admin
from .models import Message, Room

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
	list_display=['name','info','pic']
	list_editable=['info']
