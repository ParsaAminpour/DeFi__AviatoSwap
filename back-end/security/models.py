from django.db import models

class Blocked(models.Model):
    ip_address = models.CharField(max_length=13, null=True)