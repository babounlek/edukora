from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from rest_framework import serializers

from subscriptions.models import Plan
from subscriptions.serializers import PlanSerializer
from users.models import phone_validator
from users.phone import to_e164, to_local

from .models import ManualPayment, MobileMoneyAccount, MobileMoneyOperator


class PayerPhoneField(serializers.CharField):
    """
    Numéro du payeur Mobile Money. Stocké au format local à 9 chiffres, contrairement
    à users.User.phone_number passé en E.164 : ce n'est pas un identifiant de compte
    mais une donnée de transaction, transmise telle quelle à l'opérateur, et la
    convertir imposerait une migration au chemin de paiement sans rien y gagner.

    Accepte néanmoins les deux formats en entrée et normalise vers le format local :
    un appelant qui transmet `user.phone_number` (désormais E.164) est légitime, et
    le refuser produirait un 400 incompréhensible côté élève.
    """

    def __init__(self, **kwargs):
        kwargs.setdefault("max_length", 16)
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        valeur = super().to_internal_value(data)
        try:
            local = to_local(to_e164(valeur))
        except DjangoValidationError:
            raise serializers.ValidationError("Numéro de téléphone invalide.")
        phone_validator(local)
        return local


class MobileMoneyAccountSerializer(serializers.ModelSerializer):
    operator_display = serializers.CharField(source="get_operator_display", read_only=True)

    class Meta:
        model = MobileMoneyAccount
        fields = ["operator", "operator_display", "phone_number", "account_name"]


class ManualPaymentSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    operator_display = serializers.CharField(source="get_operator_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    rejection_reason_display = serializers.CharField(source="get_rejection_reason_display", read_only=True)

    class Meta:
        model = ManualPayment
        fields = [
            "id", "plan", "operator", "operator_display", "amount_expected", "amount_declared",
            "payer_phone_number", "transaction_reference", "paid_at", "status", "status_display",
            "rejection_reason", "rejection_reason_display", "created_at", "reviewed_at",
        ]


class ManualPaymentDeclareSerializer(serializers.Serializer):
    """
    Pas un ModelSerializer : `amount_expected` ne doit jamais pouvoir être fourni par
    le client, seulement recalculé depuis `plan.price` (voir mission, section 8) -
    create() délègue donc à ManualPayment.objects.declare() (models.py), qui porte
    cette règle ainsi que la normalisation de la référence et la notification SMS,
    plutôt que de dupliquer cette logique ici.
    """

    plan = serializers.PrimaryKeyRelatedField(queryset=Plan.objects.filter(is_active=True))
    operator = serializers.ChoiceField(choices=MobileMoneyOperator.choices)
    amount_declared = serializers.IntegerField(min_value=1)
    payer_phone_number = PayerPhoneField()
    transaction_reference = serializers.CharField(max_length=100, allow_blank=False, trim_whitespace=True)
    paid_at = serializers.DateTimeField(required=False, allow_null=True)
    proof = serializers.FileField(required=False, allow_null=True)

    def validate(self, attrs):
        if not MobileMoneyAccount.objects.filter(operator=attrs["operator"], active=True).exists():
            raise serializers.ValidationError({
                "operator": "Ce moyen de paiement n'est pas disponible actuellement.",
            })
        plan = attrs["plan"]
        if attrs["amount_declared"] < plan.price:
            raise serializers.ValidationError({
                "amount_declared": (
                    f"Le montant déclaré ({attrs['amount_declared']} FCFA) est inférieur au prix de "
                    f"l'offre sélectionnée ({plan.price} FCFA)."
                ),
            })
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        try:
            return ManualPayment.objects.declare(
                user=request.user,
                ip=request.META.get("REMOTE_ADDR"),
                **validated_data,
            )
        except IntegrityError as exc:
            raise serializers.ValidationError({
                "transaction_reference": "Cette transaction a déjà été déclarée pour ce moyen de paiement.",
            }) from exc
