from django.contrib import admin
from .models import UserProfile, PcapFile

admin.site.register(UserProfile)

class PcapFileAdmin(admin.ModelAdmin):
    list_display = ('user', 'filename', 'file_size', 'created_at')
    search_fields = ('filename', 'user__username')
    list_filter = ('created_at', 'user')

admin.site.register(PcapFile, PcapFileAdmin)