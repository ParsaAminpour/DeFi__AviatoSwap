from django.db import models
from django.contrib.auth.models import AbstractUser, Permission
from django.conf import settings

class Wallet(models.Model):
    address = models.CharField(max_length=42, unique=True)
    balance = models.FloatField(default=0, null=True, blank=True)
    is_zero_address = models.BooleanField()
    
    def __str__(self):
        return f'{self.address[:4]}...'


class User(AbstractUser):
    wallet = models.OneToOneField(Wallet, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.CharField(max_length=12, null=True, blank=True)
    user_agent = models.CharField(max_length=256, null=True, blank=True)
    # blocked_user = models.BooleanField(default=False, null=True, blank=True)
    profile_pic = models.ImageField(null=True, blank=True)
    about = models.TextField(max_length=256, null=True, blank=True)

    # class Meta:
    #     permissions = [

    #     ]

    @property
    def wallet_address(self):
        if self.wallet.address is not None:
            return self.wallet.address
        else:
            return ''

    @property
    def get_profile_pic(self):
        if self.profile_pic == None:
            return '/static/images/unknown.jpg'
        else:
            return self.profile_pic


    def __str__(self):
        return self.username



class PurchaseMap(models.Model):
    PAIR_CHOICES = [
        ('ETHAVI','ETH/AVI'),
        ('AVIETH','AVI/ETH'),
        ('USDTAVI','USDT/AVI'),
        ('AVIUSDT','AVI/USDT')
    ]
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    amount = models.IntegerField(null=True)
    pair = models.CharField(max_length=7, null=True, choices = PAIR_CHOICES)
    date = models.DateField(null=True)

    def __str__(self):
        return self.pair


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=256, blank=True)
    avatar = models.ImageField(blank=True)
    trade_history = models.ForeignKey(PurchaseMap, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.user.username




