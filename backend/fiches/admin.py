from django.contrib import admin

from .models import FicheGeneree, FicheItem, StatutGeneration
from .pdf import queue_fiche_pdf_generation


class FicheItemInline(admin.TabularInline):
    model = FicheItem
    extra = 0
    fields = ["ordre", "competence_item"]
    readonly_fields = ["ordre", "competence_item"]
    autocomplete_fields = ["competence_item"]

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(FicheGeneree)
class FicheGenereeAdmin(admin.ModelAdmin):
    """
    Lecture seule (support/debug) - une fiche est créée par le répétiteur lui-même
    depuis l'app, jamais authored à la main. Une seule action utile : régénérer le PDF
    d'une fiche en ECHEC (ou en repartir depuis EN_COURS si le process détaché n'a
    jamais tourné) sans repasser par l'API, même patron que
    inedit.admin.EpreuveInediteAdmin.generer_pdf_sujet.
    """

    list_display = ["titre", "owner", "cursus", "subject", "statut", "nombre_questions", "created_at"]
    list_filter = ["statut", "cursus", "subject"]
    search_fields = ["titre", "owner__phone_number"]
    readonly_fields = [
        "owner", "cursus", "subject", "themes", "titre", "difficulte", "nombre_questions",
        "statut", "sujet_pdf", "corrige_pdf", "created_at",
    ]
    inlines = [FicheItemInline]
    actions = ["regenerer_pdf"]

    def has_add_permission(self, request):
        return False

    @admin.action(description="Régénérer les PDF (sujet + corrigé)")
    def regenerer_pdf(self, request, queryset):
        queryset.update(statut=StatutGeneration.EN_COURS)
        for fiche in queryset:
            queue_fiche_pdf_generation(fiche.pk)
        self.message_user(
            request,
            f"Génération relancée en arrière-plan pour {queryset.count()} fiche(s) - "
            "actualisez la page dans quelques instants. En cas d'échec silencieux, le "
            "détail est dans logs/fiche_pdf_generation.log.",
        )
