from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('start_sniffing/', views.start_sniffing, name='start_sniffing'),
    path('stop_sniffing/', views.stop_sniffing, name='stop_sniffing'),
    path('get_packets/<str:pod_name>/', views.get_packets, name='get_packets'),
    path('testv1/<str:pod_name>/', views.capture_and_return_packets, name='testv1'),
    path('protocolstack/<str:pod_name>/', views.capture_and_return_packets_no_save, name='protocolstack'),
    path('pcap_files/', views.list_pcap_files, name='list_pcap_files'),
    path('pcap_files/<int:file_id>/download/', views.download_pcap_file, name='download_pcap_file'),
    path('pcap_files/<int:file_id>/remove/', views.remove_pcap_file, name='remove_pcap_file'),
]
