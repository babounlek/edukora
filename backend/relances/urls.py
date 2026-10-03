from django.urls import path

from . import views

app_name = "relances"

urlpatterns = [
    path("desabonner/<str:jeton>/", views.desabonner_view, name="desabonner"),
    path("desabonner-bilan/<str:jeton>/", views.desabonner_bilan_view, name="desabonner-bilan"),
    path("paiement-a-reprendre/", views.paiement_a_reprendre_view, name="paiement-a-reprendre"),
    path("push/cle/", views.push_cle_view, name="push-cle"),
    path("push/abonner/", views.push_abonner_view, name="push-abonner"),
    path("push/desabonner/", views.push_desabonner_view, name="push-desabonner"),
]
