from rest_framework import serializers

from catalog.serializers import CursusSerializer

from .models import Plan, Subscription


class PlanSerializer(serializers.ModelSerializer):
    cursus = CursusSerializer(read_only=True)
    effective_duration_days = serializers.SerializerMethodField()
    effective_price = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = [
            "id", "name", "cursus", "product_type", "price", "duration_mode", "duration_days",
            "effective_duration_days", "effective_price", "inclut_inedit",
        ]

    def get_effective_duration_days(self, obj):
        return obj.effective_duration_days()

    def get_effective_price(self, obj):
        return obj.effective_price()


class SubscriptionSerializer(serializers.ModelSerializer):
    cursus = CursusSerializer(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    plan_name = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ["id", "cursus", "expires_at", "is_active", "plan_name"]

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
