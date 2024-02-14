from . import views
from django.urls import path

urlpatterns = [
    path('decompose/', views.Decomposition.as_view(), name='tsa_decomposition')
]