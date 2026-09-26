from django.urls import path

from . import views

app_name = "relances"

urlpatterns = [
    path("desabonner/<str:jeton>/", views.desabonner_view, name="desabonner"),
    path("paiement-a-reprendre/", views.paiement_a_reprendre_view, name="paiement-a-reprendre"),
]
