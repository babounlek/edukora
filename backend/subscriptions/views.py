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
        # Filtre en Python et non en base : est_achetable() dépend de la prochaine
        # ExamSession, donc d'un calcul par plan (voir Plan.est_achetable) qu'aucun
        # filtre SQL simple n'exprime. Volume négligeable (quelques offres par
        # cursus, une soixantaine tous cursus confondus) et déjà chargé de toute
        # façon par le sérialiseur, qui expose effective_duration_days.
        return [plan for plan in qs if plan.est_achetable()]


class MySubscriptionsView(generics.ListAPIView):
    serializer_class = SubscriptionSerializer
    pagination_class = None

    def get_queryset(self):
        return (
            Subscription.objects.filter(user=self.request.user)
            .select_related("cursus", "cursus__series")
        )
