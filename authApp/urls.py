from django.urls import path,include
from .views import *
from django.contrib.auth import views as auth_views
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
urlpatterns = [
    # path('register/', RegisterView.as_view(), name='register'),
    # path('login/', LoginView.as_view(), name='login'),
    # path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('registernew/', views.register, name='registernew'),
    path("accounts/", include("django.contrib.auth.urls")),
    path("signup/", views.signup, name="signup" ),
    path("", views.home, name="home"),
    path("login/", auth_views.LoginView.as_view(), name="login"),

    
]
