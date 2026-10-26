from django.contrib import admin, messages
from django.db.models import Count, Sum
from django.utils import timezone

from .models import AttributionRevendeur, Commission, CommissionDejaAcquise, Revendeur, StatutCommission


@admin.register(Revendeur)
class RevendeurAdmin(admin.ModelAdmin):
    list_display = ["nom_affiche", "type", "code", "statut", "clients", "commissions_actives_fcfa", "created_at"]
    list_filter = ["statut", "type"]
    search_fields = ["nom_affiche", "code", "user__phone_number", "user__email"]
    autocomplete_fields = ["user"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = [
        (None, {"fields": ["user", "nom_affiche", "type", "code", "statut"]}),
        ("Rémunération", {"fields": ["taux_base_pct", "palier_seuil", "palier_taux_pct"]}),
        ("Versements", {"fields": ["operateur_versement", "numero_versement"]}),
        ("Suivi", {"fields": ["contrat_accepte_le", "notes", "created_at", "updated_at"]}),
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_clients=Count("attributions", distinct=True))

    @admin.display(description="Clients", ordering="_clients")
    def clients(self, obj):
        return obj._clients

    @admin.display(description="Commissions actives (FCFA)")
    def commissions_actives_fcfa(self, obj):
        total = obj.commissions.filter(statut=StatutCommission.ACTIVE).aggregate(t=Sum("montant_fcfa"))["t"]
        return total or 0


@admin.register(AttributionRevendeur)
class AttributionRevendeurAdmin(admin.ModelAdmin):
    list_display = ["client", "revendeur", "source", "attribue_le"]
    list_filter = ["source", "revendeur"]
    search_fields = ["client__phone_number", "client__email", "revendeur__nom_affiche", "revendeur__code"]
    autocomplete_fields = ["client", "revendeur"]

    def get_readonly_fields(self, request, obj=None):
        # Le client d'une attribution existante ne change jamais : on corrige le revendeur
        # (le journal d'administration garde qui l'a fait et quand), pas le client.
        return ["client"] if obj is not None else []


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = [
        "id", "revendeur", "client", "plan", "base_fcfa", "taux_pct", "montant_fcfa", "etat_affiche",
        "a_verifier", "created_at",
    ]
    list_filter = ["statut", "a_verifier", "revendeur", "revendeur__type"]
    search_fields = ["revendeur__nom_affiche", "revendeur__code", "client__phone_number", "client__email"]
    date_hierarchy = "created_at"
    list_select_related = ["revendeur", "client", "plan"]
    actions = ["annuler_avant_acquisition", "annuler_pour_fraude", "lever_le_drapeau"]

    def get_readonly_fields(self, request, obj=None):
        # Tout est figé à la création : une commission se corrige par annulation, jamais
        # par modification des chiffres.
        return [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description="État")
    def etat_affiche(self, obj):
        return {"EN_ATTENTE": "En attente", "ACQUISE": "Acquise"}.get(obj.etat) or obj.get_statut_display()

    def _annuler(self, request, queryset, motif, *, fraude):
        faites, refusees = 0, 0
        for commission in queryset:
            try:
                commission.annuler(motif, fraude=fraude)
                faites += 1
            except (CommissionDejaAcquise, ValueError):
                refusees += 1
        if faites:
            self.message_user(request, f"{faites} commission(s) annulée(s).", messages.SUCCESS)
        if refusees:
            self.message_user(
                request,
                f"{refusees} commission(s) non annulée(s) : déjà acquises (utilise « pour fraude ») ou déjà annulées/payées.",
                messages.WARNING,
            )

    @admin.action(description="Annuler (avant acquisition : remboursement, erreur)")
    def annuler_avant_acquisition(self, request, queryset):
        self._annuler(request, queryset, f"Annulée par {request.user} le {timezone.localdate()}", fraude=False)

    @admin.action(description="Annuler pour fraude (même après acquisition)")
    def annuler_pour_fraude(self, request, queryset):
        self._annuler(request, queryset, f"Fraude - annulée par {request.user} le {timezone.localdate()}", fraude=True)

    @admin.action(description="Lever le drapeau « à vérifier »")
    def lever_le_drapeau(self, request, queryset):
        n = queryset.filter(a_verifier=True).update(a_verifier=False)
        self.message_user(request, f"{n} commission(s) libérée(s).", messages.SUCCESS)
