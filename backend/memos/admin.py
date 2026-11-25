from django.contrib import admin

from .models import Memo, StatutMemo


@admin.register(Memo)
class MemoAdmin(admin.ModelAdmin):
    """La relecture se fait ici : l'enseignant corrige la définition, coche « relu », puis la fiche peut être publiée."""

    list_display = ("terme", "subject", "statut", "relu_par_enseignant", "gratuit", "ordre", "nb_sessions", "updated_at")
    list_filter = ("statut", "relu_par_enseignant", "gratuit", "subject", "rubrique")
    list_editable = ("gratuit", "ordre")
    search_fields = ("terme", "definition", "piege", "exercice")
    filter_horizontal = ("cursus",)
    raw_id_fields = ("theme", "sources")
    actions = ["marquer_relues_et_publier", "repasser_en_brouillon"]

    @admin.display(description="Sessions")
    def nb_sessions(self, obj):
        return len(obj.sessions or [])

    def save_model(self, request, obj, form, change):
        # Une retouche du texte dans l'administration protège la fiche d'une réécriture par l'extraction.
        if change and {"definition", "exemple", "piege", "exercice", "reponse", "rubrique", "terme"} & set(form.changed_data):
            obj.modifie_a_la_main = True
        super().save_model(request, obj, form, change)

    @admin.action(description="Marquer relues par un enseignant et publier")
    def marquer_relues_et_publier(self, request, queryset):
        for memo in queryset:
            memo.relu_par_enseignant = True
            memo.statut = StatutMemo.PUBLIE
            memo.save()

    @admin.action(description="Repasser en brouillon")
    def repasser_en_brouillon(self, request, queryset):
        queryset.update(statut=StatutMemo.BROUILLON)
