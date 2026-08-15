from django.urls import path

from . import views

app_name = "access"

urlpatterns = [
    path("read/<slug:lesson_slug>/", views.read_lesson, name="read"),
    path("preview/<slug:lesson_slug>/", views.preview_lesson, name="preview"),
    path("cours/read/<slug:cours_id>/", views.read_cours, name="cours-read"),
    path("cours/preview/<slug:cours_id>/", views.preview_cours, name="cours-preview"),
    path("progression/", views.my_progression, name="progression"),
]
