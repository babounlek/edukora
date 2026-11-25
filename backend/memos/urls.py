from django.urls import path

from . import views

app_name = "memos"

urlpatterns = [
    path("apercu/", views.apercu, name="apercu"),
    path("matieres/", views.matieres, name="matieres"),
    path("fiches/", views.liste, name="fiches"),
    path("fiches/<int:pk>/garder/", views.garder, name="garder"),
]
