from django.contrib import admin

from catalog.models import StatutContenu

from .models import (
    Blueprint, EpreuveInedite, ExerciceInedite, QuestionInedite,
    RappelDeMethodeInedite, TentativeInedite, TentativeReponse,
)
from .sujet_pdf import queue_sujet_pdf_generation

# Blueprint/EpreuveInedite sont désormais éditables, avec actions de validation - le
# pipeline existe (voir inedit.ingestion), même patron que
# quiz.admin.CompetenceItemAdmin (pas de readonly_fields, actions marquer_valide/
# marquer_brouillon). Les boutons admin équivalents à
# CompetenceItemAdmin.select_batch_view/ingestion_view (déclenchement depuis l'admin
# plutôt que la CLI) sont volontairement différés - `manage.py select_inedit_batch`/
# `ingest_inedit_content` couvrent déjà la même fonctionnalité (voir inedit.ingestion),
# et ces vues n'ajouteraient qu'une ergonomie, pas une capacité nouvelle.
#
# ExerciceInedite/QuestionInedite/TentativeInedite/TentativeReponse restent en lecture
# seule (sous-objets dérivés d'une génération, ou données de tentative élève - jamais
# authored à la main) - inchangé depuis la phase "socle données".


class ExerciceInediteInline(admin.TabularInline):
    model = ExerciceInedite
    extra = 0
    fields = ["numero_exercice", "points", "groupes"]
    readonly_fields = ["numero_exercice", "points", "groupes"]

    def has_add_permission(self, request, obj=None):
        return False


class QuestionInediteInline(admin.TabularInline):
    model = QuestionInedite
    extra = 0
    fields = ["numero", "ordre", "type_reponse", "difficulte_estimee"]
    readonly_fields = ["numero", "ordre", "type_reponse", "difficulte_estimee"]

    def has_add_permission(self, request, obj=None):
        return False


class RappelDeMethodeInediteInline(admin.TabularInline):
    model = RappelDeMethodeInedite
    extra = 0
    fields = ["competence", "cours_genere_display", "cours"]
    readonly_fields = ["competence", "cours_genere_display"]
    autocomplete_fields = ["cours"]

    @admin.display(description="Cours généré ?", boolean=True)
    def cours_genere_display(self, obj):
        return obj.cours_genere


class TentativeReponseInline(admin.TabularInline):
    model = TentativeReponse
    extra = 0
    fields = ["question", "reponse_choisie", "resultat_declare", "answered_at"]
    readonly_fields = ["question", "reponse_choisie", "resultat_declare", "answered_at"]

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Blueprint)
class BlueprintAdmin(admin.ModelAdmin):
    list_display = ["titre", "subject", "cursus_list", "statut", "external_id", "updated_at"]
    list_filter = ["statut", "subject", "cursus"]
    search_fields = ["titre", "external_id"]
    autocomplete_fields = ["subject"]  # cursus exclu : CursusAdmin n'a pas de search_fields
    filter_horizontal = ["competences", "cursus"]
    actions = ["marquer_valide", "marquer_brouillon"]

    @admin.display(description="Cursus")
    def cursus_list(self, obj):
        return ", ".join(str(c) for c in obj.cursus.all())

    @admin.action(description="Marquer comme Validé (utilisable pour une génération)")
    def marquer_valide(self, request, queryset):
        updated = queryset.update(statut=StatutContenu.VALIDE)
        self.message_user(request, f"{updated} blueprint(s) validé(s).")

    @admin.action(description="Repasser en Brouillon")
    def marquer_brouillon(self, request, queryset):
        updated = queryset.update(statut=StatutContenu.BROUILLON)
        self.message_user(request, f"{updated} blueprint(s) repassé(s) en brouillon.")


@admin.register(EpreuveInedite)
class EpreuveInediteAdmin(admin.ModelAdmin):
    list_display = [
        "titre", "blueprint", "subject", "cursus_list", "statut",
        "score_originalite", "score_qualite", "sujet_pdf_display", "updated_at",
    ]
    list_filter = ["statut", "subject", "cursus"]
    search_fields = ["titre", "external_id"]
    autocomplete_fields = ["blueprint", "subject"]  # cursus exclu, voir BlueprintAdmin
    filter_horizontal = ["cursus"]
    readonly_fields = ["sujet_pdf"]
    inlines = [ExerciceInediteInline]
    actions = ["marquer_valide", "marquer_brouillon", "generer_pdf_sujet"]

    @admin.display(description="Cursus")
    def cursus_list(self, obj):
        return ", ".join(str(c) for c in obj.cursus.all())

    @admin.display(boolean=True, description="PDF sujet")
    def sujet_pdf_display(self, obj):
        return bool(obj.sujet_pdf)

    @admin.action(description="Marquer comme Validé (publiée, visible des abonnés inédit)")
    def marquer_valide(self, request, queryset):
        updated = queryset.update(statut=StatutContenu.VALIDE)
        # Lancé en arrière-plan (voir queue_sujet_pdf_generation) plutôt qu'en
        # synchrone ici - même contrainte que catalog.admin.LessonAdmin (Playwright
        # dans un thread de requête admin s'est montré peu fiable en pratique). Ne
        # traite que les épreuves fraîchement validées qui n'ont pas encore de PDF -
        # une épreuve déjà validée précédemment (ré-incluse dans cette sélection) et
        # déjà pourvue d'un PDF n'est jamais régénérée ici (voir generer_pdf_sujet
        # pour une régénération explicite). Le corrigé, lui, ne génère jamais de PDF -
        # voir inedit.sujet_pdf (docstring de module).
        sujet_a_generer = list(queryset.filter(sujet_pdf="").values_list("pk", flat=True))
        queue_sujet_pdf_generation(sujet_a_generer)
        self.message_user(
            request,
            f"{updated} épreuve(s) validée(s) - génération du PDF du sujet lancée en "
            "arrière-plan (actualisez la page dans quelques instants).",
        )

    @admin.action(description="Repasser en Brouillon (dépubliée)")
    def marquer_brouillon(self, request, queryset):
        updated = queryset.update(statut=StatutContenu.BROUILLON)
        self.message_user(request, f"{updated} épreuve(s) repassée(s) en brouillon.")

    @admin.action(description="Générer/régénérer le PDF du sujet")
    def generer_pdf_sujet(self, request, queryset):
        pks = list(queryset.values_list("pk", flat=True))
        queue_sujet_pdf_generation(pks, force=True)
        self.message_user(
            request,
            f"Génération du PDF de sujet lancée en arrière-plan pour {len(pks)} épreuve(s) - "
            "actualisez la page dans quelques instants. En cas d'échec silencieux, le détail est "
            "dans logs/sujet_pdf_generation.log.",
        )


@admin.register(ExerciceInedite)
class ExerciceInediteAdmin(admin.ModelAdmin):
    list_display = ["epreuve", "numero_exercice", "points"]
    list_filter = ["epreuve__cursus"]
    search_fields = ["epreuve__titre", "numero_exercice"]
    # enonce_intro_markdown inclus : sans lui, ce champ apparaîtrait en textarea
    # éditable (Django expose par défaut tout champ non listé ici), en contradiction
    # avec la règle "sous-objets dérivés d'une génération, jamais authored à la main"
    # rappelée en tête de module.
    readonly_fields = ["epreuve", "numero_exercice", "points", "groupes", "enonce_intro_markdown"]
    inlines = [QuestionInediteInline, RappelDeMethodeInediteInline]

    def has_add_permission(self, request):
        return False


@admin.register(QuestionInedite)
class QuestionInediteAdmin(admin.ModelAdmin):
    list_display = ["exercice", "numero", "ordre", "type_reponse", "difficulte_estimee"]
    list_filter = ["type_reponse", "difficulte_estimee"]
    search_fields = ["exercice__epreuve__titre", "numero", "enonce_markdown"]
    readonly_fields = [
        "exercice", "numero", "ordre", "enonce_markdown", "corrige_markdown",
        "difficulte_estimee", "type_reponse", "choix", "reponse_correcte",
    ]

    def has_add_permission(self, request):
        return False


@admin.register(TentativeInedite)
class TentativeInediteAdmin(admin.ModelAdmin):
    list_display = ["user", "epreuve", "started_at", "exam_mode_started_at", "submitted_at", "score_obtenu"]
    list_filter = ["epreuve__cursus", "submitted_at"]
    search_fields = ["user__phone_number", "epreuve__titre"]
    readonly_fields = [
        "user", "epreuve", "started_at", "exam_mode_started_at", "submitted_at", "score_obtenu", "questions_marquees",
    ]
    inlines = [TentativeReponseInline]

    def has_add_permission(self, request):
        return False


@admin.register(TentativeReponse)
class TentativeReponseAdmin(admin.ModelAdmin):
    list_display = ["tentative", "question", "reponse_choisie", "resultat_declare", "est_correcte", "answered_at"]
    list_filter = ["resultat_declare", "answered_at"]
    readonly_fields = ["tentative", "question", "reponse_choisie", "resultat_declare", "temps_secondes", "answered_at"]

    def has_add_permission(self, request):
        return False
