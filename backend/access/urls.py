from django.urls import path

from . import views

app_name = "access"

urlpatterns = [
    path("read/<slug:lesson_slug>/", views.read_lesson, name="read"),
    path("preview/<slug:lesson_slug>/", views.preview_lesson, name="preview"),
    path("cours/read/<slug:cours_id>/", views.read_cours, name="cours-read"),
    path("cours/preview/<slug:cours_id>/", views.preview_cours, name="cours-preview"),
    path("cours/pdf/<slug:cours_id>/", views.download_cours_pdf, name="cours-pdf"),
    path("lessons/<int:lesson_id>/sujet.pdf", views.download_lesson_sujet_pdf, name="lesson-sujet-pdf"),
    path("telechargements/quota/", views.quota_telechargements, name="quota-telechargements"),
    path("progression/", views.my_progression, name="progression"),
    path("etude/", views.etude_marques, name="etude-marques"),
    path("etude/carnet/", views.etude_carnet, name="etude-carnet"),
    path("exercices/<int:exercise_id>/fait/", views.marquer_exercice_fait, name="exercice-fait"),
]
