from django.urls import path
from . import views

urlpatterns = [
    # path('pm2.5/', views.AirView.as_view(), name='air_pm2_5'),
    # path('laeq/', views.NoiseView.as_view(), name='noise_laeq'),
    path('air-noise/', views.AirNoiseView.as_view(), name='air_noise'),
    path('air-predictions/', views.AirPredictions.as_view(), name='air_predictions'),
    path('noise-predictions/', views.NoisePredictions.as_view(), name='noise_predictions'),
]