from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("initiate/", views.initiate_payment, name="initiate"),
    path("status/<int:transaction_id>/", views.check_payment_status, name="status"),
    path("manual/methods/", views.list_manual_payment_methods, name="manual-methods"),
    path("manual/declare/", views.declare_manual_payment, name="manual-declare"),
    path("manual/mine/", views.list_my_manual_payments, name="manual-mine"),
]
