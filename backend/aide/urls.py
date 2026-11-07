from django.urls import path

from . import views

app_name = "aide"

urlpatterns = [
    path("articles/", views.liste_articles, name="articles"),
    path("articles/<slug:slug>/", views.detail_article, name="article"),
    path("mon-code/", views.mon_code, name="mon-code"),
]
