from django.urls import path, include
from . import views

urlpatterns = [
    path('test/', views.capture_packets, name='test'),
    path('testv1/<str:pod_name>/', views.capture_and_return_packets, name='testv1'),
]