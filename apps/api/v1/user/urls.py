from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.modified_create_user, name='create_user'),
    path('list/', views.list_users, name='list_users'),
    path('update/<int:pk>/', views.update_user, name='update_user'),
    path('delete/<int:pk>/', views.delete_user, name='delete_user'),
    path('information/', views.get_user_information, name='get_user_information'),
    path('compare/cu/', views.compare_cu_config, name='compare_cu_config'),
    path('compare/du/', views.compare_du_config, name='compare_du_config'),
    path('compare/ue/', views.compare_ue_config, name='compare_ue_config'),
]
