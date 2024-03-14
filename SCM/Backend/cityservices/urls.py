from django.urls import path, include

from .views import BusRouteView,SA_energy, DublinBikesView


urlpatterns = [
    path('bus-routes/', BusRouteView.as_view(), name='bus-routes'),
    path('sa-energy/', SA_energy.as_view(), name='SA_energy'),
    path('dublin-bikes-predictions/', DublinBikesView.as_view(), name='dublin-bikes'),
]
