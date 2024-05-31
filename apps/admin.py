from django.contrib import admin
from .models import UserProfile, PcapFile

admin.site.register(UserProfile)


@admin.register(PcapFile)
class PcapFileAdmin(admin.ModelAdmin):
    list_display = ('user', 'filename', 'created_at')

