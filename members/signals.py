from .models import *
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.utils.crypto import get_random_string


@receiver(pre_save, sender=User)
def generate_otp(sender, instance, **kwargs):
    """
    Signal handler to generate a random 4-digit OTP before saving the User instance.
    """
    if not instance.otp:
        instance.otp = get_random_string(length=4, allowed_chars='0123456789')
