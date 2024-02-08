from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("sensors/", include("sensors.urls")),
    path("dublin-bikes-prediction/", include("dublinBikesPrediction.urls")),
]
