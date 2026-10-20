from rest_framework import generics, permissions

from users.parent import portee_famille
from users.profils import profil_actif

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

    def list(self, request, *args, **kwargs):
        # `?tous=1` : toute la famille, en mode parent seulement (voir users.parent.portee_famille).
        refus, self.limiter_au_profil = portee_famille(request)
        if refus is not None:
            return refus
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        abonnements = (
            Subscription.objects.filter(user=self.request.user)
            .select_related("cursus", "cursus__series", "profil")
        )
        if getattr(self, "limiter_au_profil", False):
            abonnements = abonnements.filter(profil=profil_actif(self.request))
        return abonnements
