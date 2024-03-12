from django.urls import path, include

from .views import BusRouteView,SA_energy


urlpatterns = [
    path('bus-routes/', BusRouteView.as_view(), name='bus-routes'),
    path('sa-energy/', SA_energy.as_view(), name='SA_energy'),
]
