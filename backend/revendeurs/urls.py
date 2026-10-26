from django.urls import path

from . import views

app_name = "revendeurs"

urlpatterns = [
    path("moi/", views.mon_espace, name="moi"),
    path("moi/ventes/", views.MesVentesView.as_view(), name="moi-ventes"),
    path("moi/versements/", views.MesVersementsView.as_view(), name="moi-versements"),
    path("rattachement/", views.rattachement, name="rattachement"),
]
