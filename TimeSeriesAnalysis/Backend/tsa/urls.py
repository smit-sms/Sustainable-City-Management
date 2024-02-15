from . import views
from django.urls import path

urlpatterns = [
    path('decompose/', views.Decomposition.as_view(), name='tsa_decomposition'),
    path('stationarity/', views.AdfStationarityCheck.as_view(), name='tsa_stationarity'),
    path('first_difference/', views.FirstDifference.as_view(), name='tsa_first_difference'),
    path('correlation/', views.AcfPacf.as_view(), name='tsa_correlation'),
]