from django.urls import path

from . import views, webhook

app_name = "whatsapp"

urlpatterns = [
    path("statut/", views.my_status, name="statut"),
    path("opt-in/", views.opt_in, name="opt-in"),
    path("opt-out/", views.opt_out, name="opt-out"),
    # Publique et non authentifiée (Meta n'a aucun JWT à présenter) : c'est la
    # signature du corps qui fait foi, voir webhook.verifier_signature.
    path("webhook/", webhook.webhook, name="webhook"),
]
