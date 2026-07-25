from django.urls import path

from . import views

app_name = "access"

urlpatterns = [
    path("read/<int:lesson_id>/", views.read_lesson, name="read"),
    path("preview/<int:lesson_id>/", views.preview_lesson, name="preview"),
    path("cours/read/<int:cours_id>/", views.read_cours, name="cours-read"),
    path("cours/preview/<int:cours_id>/", views.preview_cours, name="cours-preview"),
    path("progression/", views.my_progression, name="progression"),
]
