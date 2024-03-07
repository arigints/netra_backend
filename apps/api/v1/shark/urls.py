from django.urls import path, include
from . import views

urlpatterns = [
    path('test/', views.capture_packets, name='test'),
]