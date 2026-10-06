from django.urls import path

from . import views

app_name = "recherche"

urlpatterns = [
    path("", views.rechercher, name="rechercher"),
    path("completer/", views.completer, name="completer"),
]
