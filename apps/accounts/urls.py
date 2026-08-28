from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView

from .views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    ProfileView,
    RefreshView,
    RegistrationView,
)

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
    path("verify/", TokenVerifyView.as_view(), name="verify"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", ProfileView.as_view(), name="me"),
    path("password/change/", PasswordChangeView.as_view(), name="password-change"),
    path("password/reset/", PasswordResetRequestView.as_view(), name="password-reset-request"),
    path(
        "password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"
    ),
]
