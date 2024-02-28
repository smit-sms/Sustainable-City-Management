from django.urls import path, include

from .views import BusRouteView, DublinBikesView


urlpatterns = [
    path('bus-routes/', BusRouteView.as_view(), name='bus-routes'),
    path('dublin-bikes-predictions/', DublinBikesView.as_view(), name='dublin-bikes'),
]
