from django.contrib import admin

from .models import CompteurQuota, LectureProgress, ReglagesTelechargement, TelechargementPdf


@admin.register(LectureProgress)
class LectureProgressAdmin(admin.ModelAdmin):
    list_display = ["profil", "lesson", "cours", "first_read_at", "last_read_at"]
    list_filter = ["first_read_at"]
    search_fields = ["profil__compte__phone_number", "lesson__title", "cours__titre"]
    readonly_fields = ["profil", "lesson", "cours", "first_read_at", "last_read_at"]

    def has_add_permission(self, request):
        return False


@admin.register(ReglagesTelechargement)
class ReglagesTelechargementAdmin(admin.ModelAdmin):
    """Une seule ligne : les quotas quotidiens de PDF (voir access.quota). Modifiable, pas supprimable."""

    list_display = ["__str__", "actif", "fuseau"]

    def has_add_permission(self, request):
        return not ReglagesTelechargement.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CompteurQuota)
class CompteurQuotaAdmin(admin.ModelAdmin):
    """
    Statistiques d'exploitation, en lecture seule. Portées : `demandeur` (crédits pris), `refus_quota_depasse`,
    `refus_plafond_reseau`, `refus_budget_global` (refus pour dépassement), `quota_atteint` (quotas épuisés), `identites`
    (nouveaux visiteurs par réseau), `reseau`/`reseau_large`/`global_anonyme` (plafonds). Les clés réseau sont hachées.
    """

    list_display = ["jour", "portee", "cle", "nombre"]
    list_filter = ["jour", "portee"]
    ordering = ["-jour", "portee"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(TelechargementPdf)
class TelechargementPdfAdmin(admin.ModelAdmin):
    """Journal des PDF délivrés (pseudonymes uniquement), en lecture seule."""

    list_display = ["jour", "type_demandeur", "demandeur", "document", "cree_le"]
    list_filter = ["jour", "type_demandeur"]
    search_fields = ["document"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
