from django.contrib import admin
from django.contrib.auth import get_user_model
from django.http import Http404, HttpResponseRedirect
from django.urls import path, reverse

from .code_assistance import user_id_depuis_code
from .models import ArticleAide


@admin.register(ArticleAide)
class ArticleAideAdmin(admin.ModelAdmin):
    list_display = ("titre_fr", "categorie", "ordre", "populaire", "publie", "traduit", "modifie_a_la_main", "maj_le")
    list_filter = ("categorie", "publie", "populaire", "modifie_a_la_main")
    search_fields = ("slug", "titre_fr", "titre_en", "mots_cles_fr", "corps_fr")
    list_editable = ("ordre", "populaire", "publie")
    prepopulated_fields = {"slug": ("titre_fr",)}
    fieldsets = (
        (None, {"fields": ("slug", "categorie", "ordre", "populaire", "publie", "pages_liees")}),
        ("Français", {"fields": ("titre_fr", "resume_fr", "corps_fr", "mots_cles_fr")}),
        (
            "English (laisser vide si non traduit : l'article s'affiche alors en français)",
            {"fields": ("titre_en", "resume_en", "corps_en", "mots_cles_en")},
        ),
    )

    @admin.display(boolean=True, description="Traduit")
    def traduit(self, obj):
        return obj.traduit

    def save_model(self, request, obj, form, change):
        # Une correction faite ici ne doit pas être écrasée par le prochain `charger_aide`.
        obj.modifie_a_la_main = True
        super().save_model(request, obj, form, change)

    def get_urls(self):
        urls = super().get_urls()
        return [
            path("retrouver-compte/", self.admin_site.admin_view(self.retrouver_compte), name="aide_retrouver_compte"),
        ] + urls

    def retrouver_compte(self, request):
        """/admin/aide/articleaide/retrouver-compte/?code=EK-… : ouvre la fiche du compte désigné par un code d'assistance."""
        modele = get_user_model()
        user_id = user_id_depuis_code(request.GET.get("code", ""))
        utilisateur = modele.objects.filter(pk=user_id).first() if user_id else None
        if utilisateur is None:
            raise Http404("Code d'assistance inconnu ou mal recopié.")
        return HttpResponseRedirect(reverse(f"admin:{modele._meta.app_label}_{modele._meta.model_name}_change", args=[utilisateur.pk]))
