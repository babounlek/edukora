from django.urls import path

from . import views, views_candidature

app_name = "revendeurs"

urlpatterns = [
    path("moi/", views.mon_espace, name="moi"),
    path("moi/ventes/", views.MesVentesView.as_view(), name="moi-ventes"),
    path("moi/versements/", views.MesVersementsView.as_view(), name="moi-versements"),
    path("candidature/", views_candidature.candidature, name="candidature"),
    path("candidature/envoyer-code/", views_candidature.candidature_envoyer_code, name="candidature-envoyer-code"),
    path("candidature/verifier-numero/", views_candidature.candidature_verifier_numero, name="candidature-verifier-numero"),
    path("candidature/soumettre/", views_candidature.candidature_soumettre, name="candidature-soumettre"),
    path("candidature/retirer/", views_candidature.candidature_retirer, name="candidature-retirer"),
    path("rattachement/", views.rattachement, name="rattachement"),
]
