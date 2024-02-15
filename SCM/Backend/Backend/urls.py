from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("sensors/", include("sensors.urls")),
    path("energy_usage/", include("energy_usage.urls")),
]