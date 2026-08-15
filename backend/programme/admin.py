from django.contrib import admin

from .models import Module, Savoir


class SavoirInline(admin.TabularInline):
    model = Savoir
    extra = 0
    fields = ["ordre", "numero", "intitule"]


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ["classe", "serie_label", "numero", "titre", "subject", "credit_heures", "cursus_list"]
    list_filter = ["subject", "classe"]
    search_fields = ["titre", "numero"]
    filter_horizontal = ["cursus"]
    inlines = [SavoirInline]

    @admin.display(description="Cursus")
    def cursus_list(self, obj):
        return ", ".join(str(c) for c in obj.cursus.all()) or "non rattaché"


@admin.register(Savoir)
class SavoirAdmin(admin.ModelAdmin):
    list_display = ["module", "numero", "intitule"]
    search_fields = ["intitule"]
    autocomplete_fields = ["module"]
