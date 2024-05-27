from django.urls import path
from . import views

urlpatterns = [
    path('pods/', views.get_user_pods, name='get_user_pods'),
    path('deployments/', views.get_user_deployments, name='get_user_deployments'),
    path('restart_single_cu/', views.restart_single_cu, name='restart_single_cu'),
    path('restart_single_du/', views.restart_single_du, name='restart_single_du'),
    path('restart_single_ru/', views.restart_single_du, name='restart_single_ru'),
    path('restart_single_ue/', views.restart_single_ue, name='restart_single_ue'),
    path('restart_multignb_cu/', views.restart_multignb_cu, name='restart_multignb_cu'),
    path('restart_multignb_du1/', views.restart_multignb_du1, name='restart_multignb_du1'),
    path('restart_multignb_du2/', views.restart_multignb_du2, name='restart_multignb_du2'),
    path('restart_multignb_ru1/', views.restart_multignb_du1, name='restart_multignb_ru1'),
    path('restart_multignb_ru2/', views.restart_multignb_du2, name='restart_multignb_ru2'),
    path('restart_multignb_ue1/', views.restart_multignb_ue1, name='restart_multignb_ue1'),
    path('restart_multignb_ue2/', views.restart_multignb_ue2, name='restart_multignb_ue2'),
    path('restart_multiue_cu/', views.restart_multiue_cu, name='restart_multiue_cu'),
    path('restart_multiue_du/', views.restart_multiue_du, name='restart_multiue_du'),
    path('restart_multiue_ru/', views.restart_multiue_du, name='restart_multiue_ru'),
    path('restart_multiue_ue1/', views.restart_multiue_ue1, name='restart_multiue_ue1'),
    path('restart_multiue_ue2/', views.restart_multiue_ue2, name='restart_multiue_ue2'),
    path('pods/<str:pod_name>/logs/', views.get_pod_logs, name='get_pod_logs'),
    path('set_replicaset/', views.set_replicaset, name='set_replicaset'),
    path('ping_google/', views.ping_google, name='ping_google'),
    path('curl_google/', views.curl_google, name='curl_google')
]
