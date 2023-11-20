from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ThinSliceViewSet


router = DefaultRouter()
router.register('', ThinSliceViewSet, name='ThinSlice')

urlpatterns = [
    path('', include(router.urls)),
]
