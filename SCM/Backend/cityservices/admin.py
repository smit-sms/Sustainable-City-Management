from django.contrib import admin
from .models import BusRoute, BusStop, DublinBikeStation

admin.site.register(BusRoute)
admin.site.register(BusStop)
admin.site.register(DublinBikeStation)
