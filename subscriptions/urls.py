from django.urls import path

from . import views

app_name = "subscriptions"

urlpatterns = [
    path("plans/", views.PlanListView.as_view(), name="plan-list"),
    path("mine/", views.MySubscriptionsView.as_view(), name="my-subscriptions"),
]
