import json
from pathlib import Path

from django.conf import settings
from django.contrib import admin, messages
from django.shortcuts import render
from django.urls import path

from catalog.models import Country, StatutContenu

from .ingestion import SELECTION_FLOOR, SELECTION_LIMIT, run_ingestion, select_quiz_batch
from .models import CompetenceItem, QuizAnswer, QuizQuestion, QuizSession

# Sous-dossier de catalog.admin.INGEST_DIR réservé aux lots CompetenceItem du skill
# concepteur-quiz-competence - voir quiz.ingestion (docstring de module) pour la
# raison de cette convention (réutilise le bind mount Docker existant de `ingest/`
# plutôt que d'en exiger un nouveau).
QUIZ_INGEST_DIR = Path(settings.BASE_DIR) / "ingest" / "_quiz"


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
    list_display = ["theme", "subject", "difficulte_estimee", "type_reponse", "statut", "external_id", "updated_at"]
    list_filter = ["statut", "type_reponse", "difficulte_estimee", "subject"]
    search_fields = ["theme__name", "enonce_markdown", "external_id"]
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

    def get_urls(self):
        custom_urls = [
            path(
                "selection-batch/", self.admin_site.admin_view(self.select_batch_view),
                name="quiz_competenceitem_select_batch",
            ),
            path(
                "ingestion/", self.admin_site.admin_view(self.ingestion_view),
                name="quiz_competenceitem_ingestion",
            ),
        ]
        return custom_urls + super().get_urls()

    def select_batch_view(self, request):
        """
        Pendant admin de `manage.py select_quiz_batch` - sélection déterministe
        (aucun contenu inventé ici, voir quiz.ingestion.select_quiz_batch) des
        compétences sous-couvertes pour un pays donné, avec leur matériel de
        référence. N'écrit jamais de CompetenceItem : produit uniquement le JSON à
        transmettre ensuite au skill concepteur-quiz-competence (copié depuis cette
        page, ou lu depuis le fichier écrit sur disque - les deux pointent vers le
        même contenu).
        """
        requests_json = None
        output_path = None
        countries = Country.objects.filter(actif=True).order_by("label")

        if request.method == "POST":
            pays_code = request.POST.get("pays", "")
            try:
                country = Country.objects.get(code__iexact=pays_code)
            except Country.DoesNotExist:
                self.message_user(request, f"Pays inconnu : {pays_code!r}.", level=messages.ERROR)
            else:
                try:
                    limit = int(request.POST.get("limit") or SELECTION_LIMIT)
                    floor = int(request.POST.get("floor") or SELECTION_FLOOR)
                except (TypeError, ValueError):
                    limit, floor = SELECTION_LIMIT, SELECTION_FLOOR

                requests = select_quiz_batch(country, limit=limit, floor=floor)
                requests_json = json.dumps(requests, ensure_ascii=False, indent=2)

                QUIZ_INGEST_DIR.mkdir(parents=True, exist_ok=True)
                output_path = QUIZ_INGEST_DIR / f"_batch_{country.code.lower()}.json"
                output_path.write_text(requests_json, encoding="utf-8")

                if requests:
                    self.message_user(
                        request,
                        f"{len(requests)} compétence(s) sélectionnée(s) pour {country} - "
                        f"écrit dans {output_path}.",
                    )
                else:
                    self.message_user(
                        request,
                        f"Aucune compétence sous le plancher ({floor}) pour {country} - "
                        "soit tout est déjà couvert, soit aucune Question validée n'est encore taguée.",
                        level=messages.WARNING,
                    )

        context = {
            **self.admin_site.each_context(request),
            "title": "Sélection d'un lot de compétences à générer",
            "opts": self.model._meta,
            "countries": countries,
            "default_limit": SELECTION_LIMIT,
            "default_floor": SELECTION_FLOOR,
            "requests_json": requests_json,
            "output_path": output_path,
        }
        return render(request, "admin/quiz/select_batch.html", context)

    def ingestion_view(self, request):
        """
        Pendant admin de `manage.py ingest_quiz_content` - ingère tous les lots JSON
        déjà générés (par le skill concepteur-quiz-competence) sous `ingest/_quiz/
        <code_pays>/...`. Les items entrent statut=VALIDE et sont immédiatement
        servables en Quiz, sans étape de relecture humaine supplémentaire (voir
        quiz.ingestion.ingest_competence_item) - voir l'avertissement affiché sur la
        page elle-même avant de cliquer.
        """
        report = None
        if request.method == "POST":
            report = run_ingestion(QUIZ_INGEST_DIR)

        files = (
            sorted(f.relative_to(QUIZ_INGEST_DIR).as_posix() for f in QUIZ_INGEST_DIR.rglob("*.json") if f.parent.name.lower() != "_quiz")
            if QUIZ_INGEST_DIR.exists() else []
        )
        context = {
            **self.admin_site.each_context(request),
            "title": "Ingestion des lots de quiz générés",
            "opts": self.model._meta,
            "ingest_dir": QUIZ_INGEST_DIR,
            "files": files,
            "report": report,
        }
        return render(request, "admin/quiz/ingestion.html", context)
