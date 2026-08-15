from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("otp/request/", views.otp_request_view, name="otp-request"),
    path("otp/verify/", views.otp_verify_view, name="otp-verify"),
    path("google/", views.google_signin_view, name="google-signin"),
    path("google/link/", views.google_link_view, name="google-link"),
    # views.token_refresh_view (pas le TokenRefreshView stock de simplejwt) : lit le
    # refresh token depuis le cookie httpOnly posé par otp_verify_view, jamais depuis
    # le corps de la requête - voir sa docstring.
    path("token/refresh/", views.token_refresh_view, name="token-refresh"),
    path("phone/change/request/", views.phone_change_request_view, name="phone-change-request"),
    path("phone/change/confirm/", views.phone_change_confirm_view, name="phone-change-confirm"),
    path("identities/<slug:provider>/", views.unlink_identity_view, name="identity-unlink"),
    path("logout/", views.logout_view, name="logout"),
    path("me/", views.me_view, name="me"),
]
