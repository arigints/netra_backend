from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    level = models.IntegerField(default=1)
    completion = models.FloatField(default=0.0)
    session_key = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return self.user.username

# Signal to create or update user profile
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.profile.save()

# Signal for user session key
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib.sessions.models import Session

@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    # Delete previous sessions
    if hasattr(user, 'userprofile'):
        session_key = user.userprofile.session_key
        if session_key and Session.objects.filter(session_key=session_key).exists():
            Session.objects.get(session_key=session_key).delete()
    
    # Update user's session key
    user.userprofile.session_key = request.session.session_key
    user.userprofile.save()
