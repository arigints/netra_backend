from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('test/', views.capture_packets, name='test'),
    path('testv1/<str:pod_name>/', views.capture_and_return_packets, name='testv1'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)