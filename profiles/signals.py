from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to automatically create a Profile when a new User is created.

    Args:
        sender: The model class (User model)
        instance: The actual instance being saved
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal to save the Profile whenever the User is saved.

    This ensures the profile is always saved when the user is updated.

    Args:
        sender: The model class (User model)
        instance: The actual instance being saved
        **kwargs: Additional keyword arguments
    """
    # Only save if profile exists (it should after creation)
    if hasattr(instance, 'profile'):
        instance.profile.save()
