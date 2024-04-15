from django.urls import path,include
from . import views
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path("whitelist/",views.New_whitelist.as_view()),
    path('register/', views.RegisterView.as_view(), name="register"),
    path('login/', views.Loginview.as_view(), name="login"),
    path('logout/', views.LogoutView.as_view(), name = "logout"),
    path('token/', jwt_views.TokenObtainPairView.as_view(), name ="token_obtain_pair"),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
]
