from django.contrib import admin

from .models import AnalyticsEvent


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    """
    Lecture seule : voir l'audit UX, reco 5.3 - "vérifier avec de vraies données"
    veut d'abord dire pouvoir consulter ce qui a déjà été enregistré, avant tout
    outil de tableau de bord dédié.
    """

    list_display = ["name", "user", "properties", "created_at"]
    list_filter = ["name", "created_at"]
    search_fields = ["user__phone_number"]
    readonly_fields = ["name", "user", "properties", "created_at"]
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
