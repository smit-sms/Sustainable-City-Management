from django.urls import path
from . import views

urlpatterns = [
    path('snapshot/', views.ViewSnapshot.as_view(), name='bikes_snapshot'),
]