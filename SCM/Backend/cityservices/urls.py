from django.urls import path, include

from .views import BusRouteView


urlpatterns = [
    path('bus-routes/', BusRouteView.as_view(), name='bus-routes'),
]
