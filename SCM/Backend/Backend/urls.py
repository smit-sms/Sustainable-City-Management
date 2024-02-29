from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/",include("authentication.urls")),
    path("sensors/", include("sensors.urls")),
    path("city_services/", include("cityservices.urls")),
]
