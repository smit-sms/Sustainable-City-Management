from django.urls import path,include
from . import views

urlpatterns = [
    path("",views.Authenticate.as_view())
]