from rest_framework import generics, permissions

from .models import Plan, Subscription
from .serializers import PlanSerializer, SubscriptionSerializer


class PlanListView(generics.ListAPIView):
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        qs = Plan.objects.filter(is_active=True).select_related("cursus", "cursus__series", "cursus__country")
        if cursus_id := self.request.query_params.get("cursus"):
            qs = qs.filter(cursus_id=cursus_id)
        return qs


class MySubscriptionsView(generics.ListAPIView):
    serializer_class = SubscriptionSerializer
    pagination_class = None

    def get_queryset(self):
        return (
            Subscription.objects.filter(user=self.request.user)
            .select_related("cursus", "cursus__series")
        )
