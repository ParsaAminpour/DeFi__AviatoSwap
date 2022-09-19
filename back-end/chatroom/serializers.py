from rest_framework import serializers
from .models import Room, Message


class MessageSerialize(serializers.ModelSerializer):
	class Meta:
		model=Message
		fields=('message','owner')

	def validate_message(self, value):
		if len(value) > 256:
			return serializers.ValidationError('The message is too much')

		return value