from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Preferences

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_preferences(sender, instance, created, **kwargs):
    """
    Signal to create a Preferences instance whenever a new User is created.
    """
    if created:
        Preferences.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_preferences(sender, instance, **kwargs):
    """
    Signal to save the Preferences instance when the User is saved.
    """
    try:
        instance.preferences.save()
    except Preferences.DoesNotExist:
        # In case the preferences don't exist yet, create them
        Preferences.objects.create(user=instance)
