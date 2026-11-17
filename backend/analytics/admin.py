from django.contrib import admin, messages
from django.template.response import TemplateResponse

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
    actions = ["vider_tout"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.action(description="Vider TOUS les événements (irréversible, avec confirmation)", permissions=["delete"])
    def vider_tout(self, request, queryset):
        """
        Supprime la table entière, quelle que soit la sélection ou le filtre : l'action est lancée
        depuis la liste, mais « vider » ne doit pas dépendre de ce qui est coché. Une page de
        confirmation s'intercale, car rien ne permet de revenir en arrière.
        """
        if request.POST.get("vidage_confirme"):
            total, _ = AnalyticsEvent.objects.all().delete()
            self.message_user(request, f"{total} événement(s) supprimé(s).", messages.SUCCESS)
            return None
        premier = queryset.values_list("pk", flat=True).first()
        return TemplateResponse(
            request,
            "admin/analytics/confirmer_vidage.html",
            {
                **self.admin_site.each_context(request),
                "title": "Vider les événements d'analytics",
                "total": AnalyticsEvent.objects.count(),
                "premier_id": premier or "",
                "opts": self.model._meta,
            },
        )
