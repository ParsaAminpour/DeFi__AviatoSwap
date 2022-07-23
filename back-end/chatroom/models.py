from signal import default_int_handler
from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.utils import timezone
from swap.models import User

class Message(models.Model):
	message = models.CharField(max_length=256, null=True, blank=True)
	owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
	time = models.DateField(null=True, blank=True, default=timezone.now())
	def __str__(self):
		return self.message


class Room(models.Model):
	name = models.CharField(max_length=256)
	online = models.ManyToManyField(
		User, related_name='onlines')
	info = models.TextField(max_length=256, null=True, blank=True)
	message = models.ManyToManyField(Message, related_name='messages')
	pic = models.ImageField(null=True, blank=True)

	def onlines_count(self):
		return self.online.count()

	def msg_count(self):
		return self.message.count()

	def add_to_group(self, user):
		self.online.add(user)

	def remove_from_group(self, user):
		self.online.remove(user)

	def add_message_to_room(self, msg):
		self.message.add(msg)

	def remove_message(self, msg):
		self.message.remove(msg)

	def __str__(self):
		return self.name


