from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.modified_create_user, name='create_user'),
    path('list/', views.list_users, name='list_users'),
    path('update/<int:pk>/', views.update_user, name='update_user'),
    path('delete/<int:pk>/', views.delete_user, name='delete_user'),
    path('information/', views.get_user_information, name='get_user_information'),
]
