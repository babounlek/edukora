from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from users.parent import portee_famille
from users.profils import profil_actif

from .models import Campagne, DureeMode, Plan, ProductType, Subscription
from .serializers import CampagneSerializer, PlanSerializer, SubscriptionSerializer


class PlanListView(generics.ListAPIView):
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        qs = Plan.objects.filter(is_active=True).select_related("cursus", "cursus__series", "cursus__country")
        if cursus_id := self.request.query_params.get("cursus"):
            qs = qs.filter(cursus_id=cursus_id)
        return qs


class CampagneEnCoursView(APIView):
    """
    La campagne promotionnelle ouverte, ou `{"campagne": null}`. Public : sert aux pages qui
    affichent un prix sans avoir chargé de plan (bandeau, accueil, accès refusé). Les prix
    sont ceux du premier enfant, lus sur un plan Jusqu'à l'Examen concerné - la grille est
    unique (même tarif pour tous les cursus), le détail par plan reste dans /plans/.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        campagne = Campagne.objects.en_cours()
        if campagne is None:
            return Response({"campagne": None})
        plan = next(
            (
                p for p in Plan.objects.filter(
                    is_active=True, product_type=ProductType.ABONNEMENT, duration_mode=DureeMode.JUSQUA_EXAMEN,
                ).select_related("cursus")
                if campagne.concerne(p)
            ),
            None,
        )
        if plan is None:
            return Response({"campagne": None})
        tarif = plan.tarif(campagne=campagne)
        return Response({"campagne": {
            **CampagneSerializer(campagne).data,
            "prix": tarif.prix,
            "prix_reference": tarif.reference,
            "prix_enfant_supplementaire": min(plan.prix_enfant_supplementaire(), tarif.prix),
            "cursus": list(campagne.cursus.values_list("pk", flat=True)),
        }})


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
