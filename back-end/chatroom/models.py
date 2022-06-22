from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from swap.models import User

class Message(models.Model):
	message = models.CharField(max_length=256, null=True, blank=True)

	def __str__(self):
		return self.message


class Room(models.Model):
	name = models.CharField(max_length=256)
	online = models.ManyToManyField(
		User, related_name='online')
	info = models.TextField(max_length=256, null=True, blank=True)
	message = models.ManyToManyField(Message)

	def onlines(self):
		return self.online.count()

	def add_to_group(self, user):
		self.online.add(user)

	def remove_from_group(self, user):
		self.online.remove(user)

	def __str__(self):
		return self.name


