from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("lessons/", views.LessonListView.as_view(), name="lesson-list"),
    path("lessons/<slug:slug>/", views.LessonDetailView.as_view(), name="lesson-detail"),
    path("cours/", views.CoursListView.as_view(), name="cours-list"),
    path("cours/<slug:slug>/", views.CoursDetailView.as_view(), name="cours-detail"),
    path("subjects/", views.SubjectListView.as_view(), name="subject-list"),
    path("cursus/", views.CursusListView.as_view(), name="cursus-list"),
    path("countries/", views.CountryListView.as_view(), name="country-list"),
    path("temoignages/", views.TemoignageListView.as_view(), name="temoignage-list"),
    path("stats/", views.PlatformStatsView.as_view(), name="platform-stats"),
]
