from django.urls import path

from . import views

app_name = "fiches"

urlpatterns = [
    path("mes-inscriptions/", views.list_my_inscriptions_repetiteur, name="mes-inscriptions"),
    path("eligibilite/", views.eligibilite, name="eligibilite"),
    path("mes-fiches/", views.list_my_fiches, name="mes-fiches"),
    path("", views.create_fiche, name="create"),
    path("<int:fiche_id>/", views.fiche_detail, name="detail"),
    path("<int:fiche_id>/sujet.pdf", views.download_sujet_pdf, name="download-sujet-pdf"),
    path("<int:fiche_id>/corrige.pdf", views.download_corrige_pdf, name="download-corrige-pdf"),
]
