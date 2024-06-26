from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
import random

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    level = models.IntegerField(default=1)
    completion = models.FloatField(default=0.0)
    session_key = models.CharField(max_length=40, blank=True, null=True)
    cu_matches = models.IntegerField(default=0)
    du_matches = models.IntegerField(default=0)
    ue_matches = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

class PcapFile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    file_data = models.BinaryField()  # Field to store binary data
    file_size = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.filename} ({self.user.username})"

class CUConfig(models.Model):
    cuId = models.CharField(max_length=100)
    cellId = models.CharField(max_length=100)
    f1InterfaceIPadd = models.CharField(max_length=100)
    f1cuPort = models.CharField(max_length=100)
    f1duPort = models.CharField(max_length=100)
    n2InterfaceIPadd = models.CharField(max_length=100)
    n3InterfaceIPadd = models.CharField(max_length=100)
    mcc = models.CharField(max_length=100)
    mnc = models.CharField(max_length=100)
    tac = models.CharField(max_length=100)
    sst = models.CharField(max_length=100)
    amfhost = models.CharField(max_length=100)

    def __str__(self):
        return f"CU Config: {self.id}"

class DUConfig(models.Model):
    gnbId = models.CharField(max_length=100)
    duId = models.CharField(max_length=100)
    cellId = models.CharField(max_length=100)
    f1InterfaceIPadd = models.CharField(max_length=100)
    f1cuPort = models.CharField(max_length=100)
    f1duPort = models.CharField(max_length=100)
    mcc = models.CharField(max_length=100)
    mnc = models.CharField(max_length=100)
    tac = models.CharField(max_length=100)
    sst = models.CharField(max_length=100)
    usrp = models.CharField(max_length=100)
    cuHost = models.CharField(max_length=100)

    def __str__(self):
        return f"DU Config: {self.id}"

class UEConfig(models.Model):
    multusIPadd = models.CharField(max_length=100)
    rfSimServer = models.CharField(max_length=100)
    fullImsi = models.CharField(max_length=100)
    fullKey = models.CharField(max_length=100)
    opc = models.CharField(max_length=100)
    dnn = models.CharField(max_length=100)
    sst = models.CharField(max_length=100)
    sd = models.CharField(max_length=100)
    usrp = models.CharField(max_length=100)

    def __str__(self):
        return f"UE Config: {self.id}"

class UserConfiguration(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cu_config = models.ForeignKey(CUConfig, on_delete=models.CASCADE)
    du_config = models.ForeignKey(DUConfig, on_delete=models.CASCADE)
    ue_config = models.ForeignKey(UEConfig, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s Configuration"

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

        # Assign configurations based on available ids
        cu_config = CUConfig.objects.filter(id=1).first()  # Example: assign CUConfig with id=1
        du_config = DUConfig.objects.filter(id=1).first()  # Example: assign DUConfig with id=1
        ue_config = UEConfig.objects.filter(id=1).first()  # Example: assign UEConfig with id=1

        if cu_config and du_config and ue_config:
            UserConfiguration.objects.create(user=instance, cu_config=cu_config, du_config=du_config, ue_config=ue_config)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
