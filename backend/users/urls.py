from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

app_name = "users"

urlpatterns = [
    path("otp/request/", views.otp_request_view, name="otp-request"),
    path("otp/verify/", views.otp_verify_view, name="otp-verify"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", views.me_view, name="me"),
]
