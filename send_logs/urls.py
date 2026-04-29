from django.urls import path
from . import views

app_name = 'send_logs'

urlpatterns = [
    path('', views.send_log_list, name='send_log_list'),
]