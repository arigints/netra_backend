from django.contrib import admin
from .models import UserProfile, PcapFile, CUConfig, DUConfig, UEConfig, UserConfiguration

admin.site.register(UserProfile)

class PcapFileAdmin(admin.ModelAdmin):
    list_display = ('user', 'filename', 'file_size', 'created_at')
    search_fields = ('filename', 'user__username')
    list_filter = ('created_at', 'user')

admin.site.register(PcapFile, PcapFileAdmin)

class CUConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'cuId', 'cellId', 'f1InterfaceIPadd', 'f1cuPort', 'f1duPort', 'n2InterfaceIPadd', 'n3InterfaceIPadd', 'mcc', 'mnc', 'tac', 'sst', 'amfhost')
    search_fields = ('id', 'cuId', 'cellId', 'f1InterfaceIPadd')

class DUConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'gnbId', 'duId', 'cellId', 'f1InterfaceIPadd', 'f1cuPort', 'f1duPort', 'mcc', 'mnc', 'tac', 'sst', 'usrp', 'cuHost')
    search_fields = ('id', 'gnbId', 'duId', 'cellId', 'f1InterfaceIPadd')

class UEConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'multusIPadd', 'rfSimServer', 'fullImsi', 'fullKey', 'opc', 'dnn', 'sst', 'sd', 'usrp')
    search_fields = ('id', 'multusIPadd', 'rfSimServer', 'fullImsi')

class UserConfigurationAdmin(admin.ModelAdmin):
    list_display = ('user', 'cu_config', 'du_config', 'ue_config')
    search_fields = ('user__username', 'cu_config__cuId', 'du_config__duId', 'ue_config__fullImsi')

admin.site.register(CUConfig, CUConfigAdmin)
admin.site.register(DUConfig, DUConfigAdmin)
admin.site.register(UEConfig, UEConfigAdmin)
admin.site.register(UserConfiguration, UserConfigurationAdmin)