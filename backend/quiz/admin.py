from django.contrib import admin

from .models import QuizAnswer, QuizQuestion, QuizSession


class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 0
    fields = ["ordre", "question"]
    readonly_fields = ["ordre", "question"]
    autocomplete_fields = ["question"]

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
