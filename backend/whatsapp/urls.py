from django.urls import path

from . import views

app_name = "whatsapp"

urlpatterns = [
    path("statut/", views.my_status, name="statut"),
    path("opt-in/", views.opt_in, name="opt-in"),
    path("opt-out/", views.opt_out, name="opt-out"),
]
