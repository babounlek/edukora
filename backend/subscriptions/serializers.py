from rest_framework import serializers

from catalog.serializers import CursusSerializer
from users.serializers import ProfilSerializer

from .models import Campagne, Plan, Subscription, campagne_en_cours


class CampagneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campagne
        fields = ["id", "nom", "nom_en", "pourcentage", "debut", "fin"]


class PlanSerializer(serializers.ModelSerializer):
    cursus = CursusSerializer(read_only=True)
    effective_duration_days = serializers.SerializerMethodField()
    effective_price = serializers.SerializerMethodField()
    prix_reference = serializers.SerializerMethodField()
    campagne = serializers.SerializerMethodField()
    prix_enfant_supplementaire = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = [
            "id", "name", "cursus", "product_type", "price", "duration_mode", "duration_days",
            "effective_duration_days", "effective_price", "prix_reference", "campagne",
            "prix_enfant_supplementaire", "inclut_inedit",
        ]

    def get_effective_duration_days(self, obj):
        return obj.effective_duration_days()

    def _tarif(self, obj):
        """Tarif pour l'enfant `?profil=` du compte connecté si fourni (enfant
        supplémentaire de la famille = tarif remisé), sinon pour le premier profil du
        compte connecté ; tarif de référence pour un visiteur anonyme. Calculé une fois
        par plan et par requête (trois champs en dépendent), campagne lue une seule fois."""
        memo = self.context.setdefault("_tarifs", {})
        if obj.pk not in memo:
            if "_campagne" not in self.context:
                self.context["_campagne"] = campagne_en_cours()
            campagne = self.context["_campagne"]
            request = self.context.get("request")
            user = getattr(request, "user", None)
            if user is None or not user.is_authenticated:
                memo[obj.pk] = obj.tarif(campagne=campagne)
            else:
                profil = None
                if profil_id := request.query_params.get("profil"):
                    profil = user.profils.filter(pk=profil_id).first() if str(profil_id).isdigit() else None
                memo[obj.pk] = obj.tarif(user=user, profil=profil, campagne=campagne)
        return memo[obj.pk]

    def get_effective_price(self, obj):
        return self._tarif(obj).prix

    def get_prix_reference(self, obj):
        """Prix sans la campagne (barré à côté du prix réel) ; égal à `effective_price` hors campagne."""
        return self._tarif(obj).reference

    def get_campagne(self, obj):
        """La campagne qui fait réellement baisser CE prix, ou None."""
        campagne = self._tarif(obj).campagne
        return CampagneSerializer(campagne).data if campagne else None

    def get_prix_enfant_supplementaire(self, obj):
        """Enfant supplémentaire de la famille, campagne en cours comprise (elle se cumule avec la remise famille)."""
        self._tarif(obj)  # charge la campagne du contexte
        return obj.prix_enfant_supplementaire(campagne=self.context["_campagne"])


class SubscriptionSerializer(serializers.ModelSerializer):
    cursus = CursusSerializer(read_only=True)
    profil = ProfilSerializer(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    plan_name = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ["id", "cursus", "profil", "expires_at", "is_active", "plan_name", "duration_mode"]

    def get_plan_name(self, obj):
        """
        Subscription ne stocke pas de FK vers Plan (une seule ligne par (user, cursus),
        prolongée à chaque paiement - voir Subscription.extend) : le forfait affiché est
        celui du DERNIER paiement réussi l'ayant activée/prolongée, tous canaux confondus
        (Transaction Campay SUCCESSFUL ou ManualPayment APPROVED - import local pour
        éviter le cycle payments -> subscriptions -> payments, voir recompenser_parrainage
        pour le même motif). None si la ligne existe sans paiement retrouvable (ex. crédit
        de parrainage seul, qui ne référence aucun Plan).
        """
        from payments.models import ManualPaymentStatus, StatutTransaction

        dernier_paiement = max(
            (
                *obj.transactions.filter(status=StatutTransaction.SUCCESSFUL).select_related("plan"),
                *obj.manual_payments.filter(status=ManualPaymentStatus.APPROVED).select_related("plan"),
            ),
            key=lambda p: p.created_at, default=None,
        )
        return dernier_paiement.plan.name if dernier_paiement else None
