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
    mois_max = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = [
            "id", "name", "cursus", "product_type", "price", "duration_mode", "duration_days",
            "effective_duration_days", "effective_price", "prix_reference", "campagne",
            "inclut_inedit", "mois_max",
        ]

    def get_effective_duration_days(self, obj):
        """Pour un plan au mois : la durée d'UN mois (30 jours), comme `effective_price` en est le prix."""
        return obj.effective_duration_days()

    def get_mois_max(self, obj):
        """Combien de mois s'achètent en une fois (1 pour un plan qui ne se vend pas au mois) - voir Plan.mois_max."""
        return obj.mois_max()

    def _tarif(self, obj):
        """Tarif du plan, le même pour tous les enfants et les visiteurs. Calculé une fois
        par plan et par requête (trois champs en dépendent), campagne lue une seule fois."""
        memo = self.context.setdefault("_tarifs", {})
        if obj.pk not in memo:
            if "_campagne" not in self.context:
                self.context["_campagne"] = campagne_en_cours()
            memo[obj.pk] = obj.tarif(campagne=self.context["_campagne"])
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
