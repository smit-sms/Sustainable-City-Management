from django.urls import path,include
from . import views

urlpatterns = [
    path("login",views.Authenticate.as_view(), name="authentication_login"),
    path("signup",views.Signup.as_view(), name="authentication_signup"),
    path("whitelist",views.New_whitelist.as_view(), name="authentication_whitelist"),
    path("get",views.get_user.as_view(), name="authentication_get"),
    path("is_authenticated",views.IsAuthenticated.as_view(), name="authentication_is_authenticated")
]
