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
