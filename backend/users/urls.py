from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("otp/request/", views.otp_request_view, name="otp-request"),
    path("otp/verify/", views.otp_verify_view, name="otp-verify"),
    path("google/", views.google_signin_view, name="google-signin"),
    path("google/link/", views.google_link_view, name="google-link"),
    path("email/request/", views.email_code_request_view, name="email-request"),
    path("email/verify/", views.email_code_verify_view, name="email-verify"),
    path("email/link/request/", views.email_link_request_view, name="email-link-request"),
    path("email/link/confirm/", views.email_link_confirm_view, name="email-link-confirm"),
    # views.token_refresh_view (pas le TokenRefreshView stock de simplejwt) : lit le
    # refresh token depuis le cookie httpOnly posé par otp_verify_view, jamais depuis
    # le corps de la requête - voir sa docstring.
    path("token/refresh/", views.token_refresh_view, name="token-refresh"),
    path("phone/change/request/", views.phone_change_request_view, name="phone-change-request"),
    path("phone/change/confirm/", views.phone_change_confirm_view, name="phone-change-confirm"),
    path("identities/<slug:provider>/", views.unlink_identity_view, name="identity-unlink"),
    path("logout/", views.logout_view, name="logout"),
    path("me/", views.me_view, name="me"),
    path("profils/", views.profils_view, name="profils"),
    path("profils/<int:profil_id>/", views.profil_detail_view, name="profil-detail"),
    path("profils/<int:profil_id>/activer/", views.activer_profil_view, name="profil-activer"),
    path("parent/verifier/", views.parent_verifier_view, name="parent-verifier"),
    path("parent/pin/", views.parent_pin_view, name="parent-pin"),
    path("parent/reinitialiser/demander/", views.parent_reinitialiser_demander_view, name="parent-reinit-demander"),
    path("parent/reinitialiser/confirmer/", views.parent_reinitialiser_confirmer_view, name="parent-reinit-confirmer"),
    path("profils/<int:profil_id>/pin/", views.profil_pin_view, name="profil-pin"),
    path("profils/<int:profil_id>/connexion/demander/", views.profil_connexion_demander_view, name="profil-connexion-demander"),
    path("profils/<int:profil_id>/connexion/confirmer/", views.profil_connexion_confirmer_view, name="profil-connexion-confirmer"),
    path("profils/<int:profil_id>/connexion/", views.profil_connexion_supprimer_view, name="profil-connexion-supprimer"),
]
