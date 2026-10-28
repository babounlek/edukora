from django.contrib import admin
from django.utils import timezone

from .models import Campagne, InscriptionInedite, InscriptionRepetiteur, ParrainageRecompense, Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ["name", "cursus", "product_type", "price", "duration_mode", "duration_days", "is_active"]
    list_filter = ["is_active", "product_type", "duration_mode", "cursus"]
    search_fields = ["name"]


@admin.register(Campagne)
class CampagneAdmin(admin.ModelAdmin):
    list_display = ["nom", "pourcentage", "debut", "fin", "active", "etat", "paiements"]
    list_filter = ["active"]
    filter_horizontal = ["cursus"]

    @admin.display(description="État")
    def etat(self, obj):
        maintenant = timezone.now()
        if not obj.active:
            return "Suspendue"
        if maintenant < obj.debut:
            return "À venir"
        return "En cours" if maintenant < obj.fin else "Terminée"

    @admin.display(description="Paiements validés")
    def paiements(self, obj):
        return (
            obj.transactions.filter(status="SUCCESSFUL").count()
            + obj.manual_payments.filter(status="APPROVED").count()
        )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "cursus", "expires_at", "is_active", "updated_at"]
    list_filter = ["cursus"]
    search_fields = ["user__phone_number"]

    @admin.display(boolean=True, description="Active")
    def is_active(self, obj):
        return obj.is_active


@admin.register(InscriptionInedite)
class InscriptionInediteAdmin(admin.ModelAdmin):
    list_display = ["user", "cursus", "expires_at", "is_active", "updated_at"]
    list_filter = ["cursus"]
    search_fields = ["user__phone_number"]

    @admin.display(boolean=True, description="Active")
    def is_active(self, obj):
        return obj.is_active


@admin.register(InscriptionRepetiteur)
class InscriptionRepetiteurAdmin(admin.ModelAdmin):
    list_display = ["user", "cursus", "expires_at", "is_active", "updated_at"]
    list_filter = ["cursus"]
    search_fields = ["user__phone_number"]

    @admin.display(boolean=True, description="Active")
    def is_active(self, obj):
        return obj.is_active


@admin.register(ParrainageRecompense)
class ParrainageRecompenseAdmin(admin.ModelAdmin):
    list_display = ["parrain", "filleul", "cursus", "montant_offert", "montant_restant", "expires_at", "created_at"]
    list_filter = ["cursus"]
    search_fields = ["parrain__phone_number", "filleul__phone_number"]

    def has_add_permission(self, request):
        return False
