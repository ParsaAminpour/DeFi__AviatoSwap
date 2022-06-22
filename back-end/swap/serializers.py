from genericpath import exists
from rest_framework import serializers
from yaml import serialize
from .models import User, Wallet
import re

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username',' email', 'password1', 'password2')

    def validate(self, data):                                                                                                                                                                                                                           
        if data.get('password1') != data.get('password2'):
            raise serializers.ValidationError('passwords are NOT same')
        return data

    def validate_username(self, value):
        existence = User.objects.filter(username = value).exists()
        if existence:
            raise serializers.ValidationError('This username used before')
        return value

    def validate_email(self, value):
        pattern = r'^[a-z]+(?:(?:\.[a-z]+)+\d*|(?:_[a-z]+)+(?:\.\d+)?)?@(?!.*\.\.)[^\W_][a-z\d.]+[a-z\d]{2}$'
        result = re.match(pattern, value)
        if not bool(result):
            raise serializers.ValidationError('The email is invalid')
        return value



class walletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ('address','balance','is_zero_address')

    def validate(self, data):
        if len(data.get('address')) > 43:
            raise serializers.ValidationError('The wallet address is invalid')
        return data

    def validate_balance(self, value):
        if value < 0:
            raise serializers.ValidationError('The balance is NOT standard')
        return value

    def validate_address(self, value):
        if value[:-3] == 'EaD':
            raise serializers.ValidationError('The wallet address is invalid')
        return value


