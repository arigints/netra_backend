from django.urls import path, include
from . import views

urlpatterns = [
    path('create_all_components/', views.create_all_components, name='create_all_components'),
]