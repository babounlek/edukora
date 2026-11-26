from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("config/", views.payment_config, name="config"),
    path("initiate/", views.initiate_payment, name="initiate"),
    path("status/<int:transaction_id>/", views.check_payment_status, name="status"),
    path("en-cours/", views.payment_en_cours, name="en-cours"),
    path("mine/", views.list_my_transactions, name="mine"),
    path("manual/methods/", views.list_manual_payment_methods, name="manual-methods"),
    path("manual/declare/", views.declare_manual_payment, name="manual-declare"),
    path("manual/mine/", views.list_my_manual_payments, name="manual-mine"),
]
