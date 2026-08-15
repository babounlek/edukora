from django.contrib import admin

from .models import InscriptionInedite, InscriptionRepetiteur, ParrainageRecompense, Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ["name", "cursus", "product_type", "price", "duration_mode", "duration_days", "is_active"]
    list_filter = ["is_active", "product_type", "duration_mode", "cursus"]
    search_fields = ["name"]


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
    list_display = ["parrain", "filleul", "cursus", "jours_offerts", "created_at"]
    search_fields = ["parrain__phone_number", "filleul__phone_number"]

    def has_add_permission(self, request):
        return False
