from django.urls import path,include
from . import views

urlpatterns = [
    path("authenticate",views.Authenticate.as_view()),
    path("signup",views.Signup.as_view()),
    path("whitelist",views.New_whitelist.as_view()),
    path("get",views.get_user.as_view()),
    path("update",views.Update_account.as_view()),
    path("is_authenticated",views.IsAuthenticated.as_view())
]