from django.contrib import admin

from catalog.models import StatutContenu

from .models import CompetenceItem, QuizAnswer, QuizQuestion, QuizSession


class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 0
    fields = ["ordre", "question", "competence_item"]
    readonly_fields = ["ordre", "question", "competence_item"]
    autocomplete_fields = ["question", "competence_item"]

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    list_display = ["user", "mode", "cursus", "subject", "theme", "started_at", "completed_at"]
    list_filter = ["mode", "cursus", "completed_at"]
    search_fields = ["user__phone_number"]
    readonly_fields = ["user", "cursus", "subject", "theme", "mode", "started_at", "completed_at"]
    inlines = [QuizQuestionInline]

    def has_add_permission(self, request):
        return False


@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ["quiz_question", "reponse_choisie", "resultat_declare", "est_correcte", "answered_at"]
    list_filter = ["resultat_declare", "answered_at"]
    readonly_fields = ["quiz_question", "reponse_choisie", "resultat_declare", "temps_secondes", "answered_at"]

    def has_add_permission(self, request):
        return False


@admin.register(CompetenceItem)
class CompetenceItemAdmin(admin.ModelAdmin):
    list_display = ["theme", "subject", "difficulte_estimee", "type_reponse", "statut", "updated_at"]
    list_filter = ["statut", "type_reponse", "difficulte_estimee", "subject"]
    search_fields = ["theme__name", "enonce_markdown"]
    autocomplete_fields = ["theme", "subject"]
    filter_horizontal = ["cursus", "source_exercises"]
    actions = ["marquer_valide", "marquer_brouillon"]

    @admin.action(description="Marquer comme Validé (entre dans le pool de quiz)")
    def marquer_valide(self, request, queryset):
        updated = queryset.update(statut=StatutContenu.VALIDE)
        self.message_user(request, f"{updated} item(s) validé(s).")

    @admin.action(description="Repasser en Brouillon (sort du pool de quiz)")
    def marquer_brouillon(self, request, queryset):
        updated = queryset.update(statut=StatutContenu.BROUILLON)
        self.message_user(request, f"{updated} item(s) repassé(s) en brouillon.")
