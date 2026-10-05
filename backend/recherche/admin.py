from django.contrib import admin

from .models import EntreeRecherche, RechercheSansResultat


@admin.register(RechercheSansResultat)
class RechercheSansResultatAdmin(admin.ModelAdmin):
    """Ce que les élèves cherchent et que le catalogue ne contient pas - le tri par défaut
    (les plus fréquentes d'abord) donne directement la liste des contenus à produire. Supprimer
    une ligne une fois le contenu ajouté remet son compteur à zéro."""

    list_display = ("requete", "pays_code", "nb", "derniere_fois")
    list_filter = ("pays_code",)
    search_fields = ("requete",)
    ordering = ("-nb", "-derniere_fois")
    readonly_fields = ("requete", "pays_code", "nb", "premiere_fois", "derniere_fois")

    def has_add_permission(self, request):
        return False


@admin.register(EntreeRecherche)
class EntreeRechercheAdmin(admin.ModelAdmin):
    """Lecture seule : l'index se reconstruit avec `manage.py indexer_recherche`, jamais à la main."""

    list_display = ("titre", "type", "matiere", "annee", "tous_cursus", "poids")
    list_filter = ("type", "pays", "tous_cursus")
    search_fields = ("titre", "titre_norm")
    list_select_related = ("matiere",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
