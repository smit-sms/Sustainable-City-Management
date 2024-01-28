from django.urls import path
from . import views

urlpatterns = [
    path('pm2.5/', views.air_pm2_5, name='air_pm2_5'),
]