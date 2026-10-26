from django.conf import settings
from django.db.models import Count, Q, Sum
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle

from .models import (
    SEUIL_VERSEMENT_FCFA,
    AttributionRevendeur,
    Commission,
    StatutCommission,
    StatutVersement,
    TypeRevendeur,
    Versement,
)
from .services import a_deja_paye, masquer_client, rattacher_tardivement, reprises_dues, ventes_du_mois


class RattachementThrottle(SimpleRateThrottle):
    """Plafond de saisies de code par compte : écarte quelqu'un qui essaierait des codes un à un
    pour en trouver un valable. Même interrupteur que les autres garde-fous de débit (coupé
    pendant `manage.py test`, voir settings.THROTTLE_PDF_ACTIF)."""

    scope = "rattachement_revendeur"
    rate = "10/hour"

    def allow_request(self, request, view):
        # Seules les saisies comptent : la page de paiement lit l'état (GET) à chaque ouverture.
        if request.method != "POST" or not getattr(settings, "THROTTLE_PDF_ACTIF", True):
            return True
        return super().allow_request(request, view)

    def get_cache_key(self, request, view):
        return self.cache_format % {"scope": self.scope, "ident": f"u{request.user.pk}"}


def _revendeur_de(user):
    return getattr(user, "revendeur", None)


def _pas_revendeur():
    return Response({"code": "pas_revendeur"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
def mon_espace(request):
    """Tableau de bord du revendeur connecté : code, taux, palier, montants par état."""
    revendeur = _revendeur_de(request.user)
    if revendeur is None:
        return _pas_revendeur()

    maintenant = timezone.now()
    actives = Commission.objects.filter(revendeur=revendeur, statut=StatutCommission.ACTIVE)
    libres = Q(a_verifier=False)
    totaux = actives.aggregate(
        en_attente=Sum("montant_fcfa", filter=libres & Q(acquise_le__gt=maintenant)),
        acquise=Sum("montant_fcfa", filter=libres & Q(acquise_le__lte=maintenant)),
        retenue=Sum("montant_fcfa", filter=Q(a_verifier=True)),
    )
    payee = Commission.objects.filter(revendeur=revendeur, statut=StatutCommission.PAYEE).aggregate(t=Sum("montant_fcfa"))["t"]

    palier = None
    if revendeur.type == TypeRevendeur.COMMERCIAL and revendeur.palier_seuil is not None:
        palier = {"seuil": revendeur.palier_seuil, "taux_pct": revendeur.palier_taux_pct}

    return Response({
        "nom_affiche": revendeur.nom_affiche,
        "type": revendeur.type,
        "code": revendeur.code,
        "statut": revendeur.statut,
        "taux_base_pct": revendeur.taux_base_pct,
        "palier": palier,
        "ventes_du_mois": ventes_du_mois(revendeur, maintenant),
        "nb_clients": AttributionRevendeur.objects.filter(revendeur=revendeur).aggregate(n=Count("id"))["n"],
        "montants": {
            "en_attente": totaux["en_attente"] or 0,
            "acquise": totaux["acquise"] or 0,
            "retenue": totaux["retenue"] or 0,
            "payee": payee or 0,
        },
        # Commissions déjà payées puis annulées pour fraude : déduites de son prochain versement.
        "seuil_versement": SEUIL_VERSEMENT_FCFA,
        "reprises_en_cours": reprises_dues(revendeur).aggregate(t=Sum("montant_fcfa"))["t"] or 0,
    })


class VenteSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField()
    plan = serializers.CharField(source="plan.name")
    etat = serializers.SerializerMethodField()

    class Meta:
        model = Commission
        fields = ["id", "created_at", "client", "plan", "base_fcfa", "taux_pct", "montant_fcfa", "etat"]

    def get_client(self, obj):
        return masquer_client(obj.client)

    def get_etat(self, obj):
        # Le motif de la retenue reste interne ; le revendeur voit seulement « retenue ».
        if obj.statut == StatutCommission.ACTIVE and obj.a_verifier:
            return "RETENUE"
        return obj.etat


class MesVentesView(ListAPIView):
    serializer_class = VenteSerializer

    def get_queryset(self):
        revendeur = _revendeur_de(self.request.user)
        if revendeur is None:
            return Commission.objects.none()
        return Commission.objects.filter(revendeur=revendeur).select_related("client", "plan").order_by("-created_at")

    def list(self, request, *args, **kwargs):
        if _revendeur_de(request.user) is None:
            return _pas_revendeur()
        return super().list(request, *args, **kwargs)


@api_view(["GET", "POST"])
@throttle_classes([RattachementThrottle])
def rattachement(request):
    """
    Saisie d'un code revendeur par un compte existant, tant qu'il n'a ni revendeur ni paiement
    validé (voir services.rattacher_tardivement). Une seule réponse d'échec, quelle qu'en soit
    la cause : on ne révèle pas si un code existe.
    """
    attribution = AttributionRevendeur.objects.filter(client=request.user).select_related("revendeur").first()

    if request.method == "GET":
        return Response({
            "peut_saisir_code": attribution is None and not a_deja_paye(request.user),
            "revendeur": {"nom_affiche": attribution.revendeur.nom_affiche} if attribution else None,
        })

    attribution = rattacher_tardivement(request.user, request.data.get("code", ""))
    if attribution is None:
        return Response({"code": "code_invalide"}, status=status.HTTP_400_BAD_REQUEST)
    return Response(
        {"revendeur": {"nom_affiche": attribution.revendeur.nom_affiche}}, status=status.HTTP_201_CREATED,
    )


class VersementSerializer(serializers.ModelSerializer):
    reference = serializers.SerializerMethodField()

    class Meta:
        model = Versement
        fields = ["id", "periode", "montant_brut", "montant_reprises", "montant_net", "statut", "operateur", "reference", "paye_le"]

    def get_reference(self, obj):
        # La référence n'existe qu'une fois l'argent envoyé.
        return obj.reference_mobile_money if obj.statut == StatutVersement.PAYE else ""


class MesVersementsView(ListAPIView):
    serializer_class = VersementSerializer

    def get_queryset(self):
        revendeur = _revendeur_de(self.request.user)
        if revendeur is None:
            return Versement.objects.none()
        return Versement.objects.filter(revendeur=revendeur).exclude(statut=StatutVersement.ANNULE).order_by("-prepare_le")

    def list(self, request, *args, **kwargs):
        if _revendeur_de(request.user) is None:
            return _pas_revendeur()
        return super().list(request, *args, **kwargs)
