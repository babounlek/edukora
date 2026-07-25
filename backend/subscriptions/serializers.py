from rest_framework import serializers

from catalog.serializers import CursusSerializer

from .models import Plan, Subscription


class PlanSerializer(serializers.ModelSerializer):
    cursus = CursusSerializer(read_only=True)
    effective_duration_days = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = ["id", "name", "cursus", "price", "duration_mode", "duration_days", "effective_duration_days"]

    def get_effective_duration_days(self, obj):
        return obj.effective_duration_days()


class SubscriptionSerializer(serializers.ModelSerializer):
    cursus = CursusSerializer(read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Subscription
        fields = ["id", "cursus", "expires_at", "is_active"]
