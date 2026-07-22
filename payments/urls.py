from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("initiate/", views.initiate_payment, name="initiate"),
    path("status/<int:transaction_id>/", views.check_payment_status, name="status"),
]
