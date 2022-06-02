from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from .models import User, Profile

@receiver(post_save, sender=User, dispatch_uid='creating_profile_for_user')
def CreatingProfileSignal(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance
        )