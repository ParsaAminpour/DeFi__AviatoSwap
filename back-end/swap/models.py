from django.db import models
from django.contrib.auth.models import AbstractUser



class Wallet(models.Model):
    address = models.CharField(max_length=42, unique=True)
    balance = models.FloatField(default=0)
    is_valid = models.BooleanField()
    is_zero_address = models.BooleanField()

    def __str__(self):
        return f'{self.address[:4]}...'

class User(AbstractUser):
    wallet = models.OneToOneField(Wallet, on_delete=models.CASCADE, null=True)
    ip_address = models.CharField(max_length=12)
    user_agent = models.CharField(max_length=256)
    blocked_user = models.BooleanField(null=True)

    def blocking_user(self):
        if not self.blocked_user:
            self.blocked_user = True
        else: pass
        self.save()
    
    def unblocking_user(self):
        if self.blocked_user:
            self.blocked_user = False
        else: pass
        self.save()

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




