from django.urls import path
from . import views

urlpatterns = [
    path('', views.SA_energy.as_view(), name='SA_energy'),
]