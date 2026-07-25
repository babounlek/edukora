from pathlib import Path

from django.conf import settings
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.shortcuts import render
from django.urls import path

from .ingestion import run_ingestion
from .models import Cours, Country, Cursus, ExamSession, Exercise, Figure, Lesson, RappelDeMethode, Series, StatutContenu, Subject, Tag
from .sujet_pdf import queue_sujet_pdf_generation

# Phrase à taper pour confirmer la purge (voir LessonAdmin.purge_view) - une action qui
# efface tout le contenu ne doit jamais être déclenchable par un simple clic accidentel.
PURGE_CONFIRMATION_PHRASE = "SUPPRIMER TOUT"

# Dossier surveillé par la tâche planifiée qui dépose les JSON produits par la
# compétence correction-experte - voir catalog.ingestion.run_ingestion.
INGEST_DIR = Path(settings.BASE_DIR) / "ingest"


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ["code", "label", "dial_code", "currency"]
    search_fields = ["code", "label"]


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ["code", "label", "country"]
    list_filter = ["country"]
    search_fields = ["code", "label"]


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ["code", "label", "country"]
    list_filter = ["country"]
    search_fields = ["code", "label"]


@admin.register(Cursus)
class CursusAdmin(admin.ModelAdmin):
    list_display = ["country", "examen", "series"]
    list_filter = ["country", "examen"]


@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = ["examen", "annee", "country", "date_debut"]
    list_filter = ["country", "examen"]
    ordering = ["-annee", "examen"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


class ExerciseInline(admin.TabularInline):
    model = Exercise
    extra = 0
    fields = ["numero_exercice", "points", "difficulte_estimee", "statut"]
    show_change_link = True


class RappelDeMethodeInline(admin.TabularInline):
    model = RappelDeMethode
    extra = 0
    fields = ["competence", "cours_genere_display", "cours"]
    readonly_fields = ["competence", "cours_genere_display"]
    autocomplete_fields = ["cours"]

    @admin.display(description="Cours généré ?", boolean=True)
    def cours_genere_display(self, obj):
        return obj.cours_genere


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ["title", "subject", "cursus_list", "lesson_type", "origine", "year", "statut", "updated_at"]
    list_filter = ["statut", "lesson_type", "origine", "subject", "cursus"]
    search_fields = ["title", "epreuve_source"]
    filter_horizontal = ["cursus", "themes", "mots_cles_recherche"]
    inlines = [ExerciseInline]
    actions = ["compiler_depuis_exercices", "generer_pdf_sujet"]

    def get_urls(self):
        custom_urls = [
            path("ingestion/", self.admin_site.admin_view(self.ingestion_view), name="catalog_lesson_ingestion"),
            path("purger/", self.admin_site.admin_view(self.purge_view), name="catalog_lesson_purge"),
        ]
        return custom_urls + super().get_urls()

    def ingestion_view(self, request):
        """
        Lance run_ingestion() sur INGEST_DIR - le pendant, depuis l'admin, de
        `manage.py ingest_corrections ingest/` : évite d'avoir à ouvrir un terminal
        pour injecter les fichiers déposés par correction-experte.
        """
        report = None
        if request.method == "POST":
            report = run_ingestion(INGEST_DIR)
            # Même logique que la commande `ingest_corrections` : ne pas laisser une
            # leçon fraîchement ingérée sans PDF de sujet en attendant qu'on pense à
            # relancer generate_sujet_pdfs séparément. Mais - contrairement à un essai
            # précédent qui appelait save_sujet_pdf() ici même, en synchrone - jamais
            # Playwright dans ce thread de requête : ça s'est montré peu fiable en
            # pratique (voir sujet_pdf.save_sujet_pdf). On délègue donc à un processus
            # détaché (voir queue_sujet_pdf_generation), le même pattern déjà fiable
            # pour la tâche planifiée qui appelle `ingest_corrections` en CLI.
            #
            # Bornée aux leçons touchées par CE run (report["lesson_ids"]) : le
            # rattrapage du retard historique reste le travail de
            # `manage.py generate_sujet_pdfs` (ou `ingest_corrections` en CLI).
            lessons_a_traiter = Lesson.objects.filter(
                pk__in=report["lesson_ids"], statut=StatutContenu.VALIDE, sujet_pdf="",
            )
            report["pdf_en_cours"] = list(lessons_a_traiter.values_list("pk", flat=True))
            queue_sujet_pdf_generation(report["pdf_en_cours"])

        # rglob (récursif), pas glob : doit lister exactement ce que run_ingestion()
        # va traiter (voir catalog.ingestion.run_ingestion, qui parcourt aussi les
        # sous-répertoires) - un fichier posé dans un sous-dossier (convention actuelle :
        # un sous-dossier par épreuve, pour regrouper le JSON et ses PNG de figures)
        # doit apparaître ici, pas seulement être traité en silence au clic. Chemin
        # relatif (pas juste .name) pour qu'un fichier dans un sous-dossier reste
        # distinguable d'un fichier du même nom ailleurs.
        files = (
            sorted(f.relative_to(INGEST_DIR).as_posix() for f in INGEST_DIR.rglob("*.json"))
            if INGEST_DIR.exists() else []
        )
        context = {
            **self.admin_site.each_context(request),
            "title": "Ingestion des contenus",
            "opts": self.model._meta,
            "ingest_dir": INGEST_DIR,
            "files": files,
            "report": report,
        }
        return render(request, "admin/catalog/ingestion.html", context)

    def purge_view(self, request):
        """
        Supprime tout le contenu pédagogique (Lesson, Exercise, Figure,
        RappelDeMethode, Cours) et les fichiers associés (PDF de sujet, images de
        figures) - jamais le référentiel (Subject/Series/Cursus/Tag), qui structure
        le contenu plutôt que d'en être. Réservé aux super-utilisateurs et requiert
        une phrase tapée à la main (pas un simple clic) : la conséquence - tout
        reperdre - ne doit jamais être déclenchable par erreur.
        """
        if not request.user.is_superuser:
            raise PermissionDenied("Réservé aux super-utilisateurs.")

        counts = {
            "lessons": Lesson.objects.count(),
            "exercises": Exercise.objects.count(),
            "figures": Figure.objects.count(),
            "cours": Cours.objects.count(),
        }

        result = None
        error = None

        if request.method == "POST":
            if request.POST.get("confirmation", "").strip() != PURGE_CONFIRMATION_PHRASE:
                error = f"Phrase de confirmation incorrecte - tapez exactement « {PURGE_CONFIRMATION_PHRASE} »."
            else:
                # Chemins relevés avant suppression : une fois les lignes supprimées,
                # le nom du fichier stocké dans le FieldFile n'est plus accessible.
                figure_paths = list(Figure.objects.exclude(image="").values_list("image", flat=True))
                pdf_paths = list(Lesson.objects.exclude(sujet_pdf="").values_list("sujet_pdf", flat=True))

                # Exercise d'abord : sa FK vers Lesson est PROTECT (voir catalog.models) -
                # supprimer les Lesson en premier lèverait ProtectedError. Cascade déjà
                # Figure et RappelDeMethode (CASCADE sur Exercise des deux côtés), donc
                # rien de plus à faire pour eux avant de passer aux Lesson puis aux Cours.
                Exercise.objects.all().delete()
                Lesson.objects.all().delete()
                Cours.objects.all().delete()

                fichiers_supprimes = 0
                for storage_path in [*figure_paths, *pdf_paths]:
                    try:
                        if default_storage.exists(storage_path):
                            default_storage.delete(storage_path)
                            fichiers_supprimes += 1
                    except OSError:
                        pass

                result = {**counts, "fichiers": fichiers_supprimes}
                counts = {"lessons": 0, "exercises": 0, "figures": 0, "cours": 0}

        context = {
            **self.admin_site.each_context(request),
            "title": "Purger tout le contenu",
            "opts": self.model._meta,
            "counts": counts,
            "confirmation_phrase": PURGE_CONFIRMATION_PHRASE,
            "result": result,
            "error": error,
        }
        return render(request, "admin/catalog/purge.html", context)

    @admin.display(description="Cursus")
    def cursus_list(self, obj):
        return ", ".join(str(c) for c in obj.cursus.all())

    @admin.action(description="Compiler le contenu depuis les exercices validés")
    def compiler_depuis_exercices(self, request, queryset):
        for lesson in queryset:
            lesson.compile_from_exercises()
        self.message_user(request, f"{queryset.count()} leçon(s) compilée(s).")

    @admin.action(description="Générer le PDF du sujet (énoncés uniquement)")
    def generer_pdf_sujet(self, request, queryset):
        # Lancé en arrière-plan (voir queue_sujet_pdf_generation) plutôt qu'en
        # synchrone ici : Playwright dans le thread d'une requête admin s'est montré
        # peu fiable en pratique (voir sujet_pdf.save_sujet_pdf). --force car un
        # déclenchement manuel explicite sur une sélection vise aussi bien à
        # régénérer un PDF existant (ex. après correction du contenu) qu'à en créer
        # un nouveau.
        pks = list(queryset.values_list("pk", flat=True))
        queue_sujet_pdf_generation(pks, force=True)
        self.message_user(
            request,
            f"Génération du PDF de sujet lancée en arrière-plan pour {len(pks)} leçon(s) - "
            "actualisez la page dans quelques instants pour voir le résultat. En cas d'échec "
            "silencieux (le PDF n'apparaît jamais), le détail est dans logs/sujet_pdf_generation.log.",
        )


class FigureInline(admin.TabularInline):
    model = Figure
    extra = 0
    fields = ["external_id", "image", "type_figure", "indispensable", "lisibilite", "origine"]


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ["lesson", "numero_exercice", "difficulte_estimee", "statut", "updated_at"]
    list_filter = ["statut", "difficulte_estimee"]
    search_fields = ["lesson__title", "lesson__epreuve_source", "enonce_markdown"]
    filter_horizontal = ["themes", "mots_cles_recherche"]
    autocomplete_fields = ["lesson"]
    inlines = [RappelDeMethodeInline, FigureInline]


@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):
    list_display = ["titre", "subject", "cursus_list", "sous_theme", "statut", "updated_at"]
    list_filter = ["statut", "subject", "cursus"]
    search_fields = ["titre", "sous_theme", "external_id"]
    filter_horizontal = ["cursus", "tags"]
    actions = ["compiler_depuis_sections"]

    @admin.display(description="Cursus")
    def cursus_list(self, obj):
        return ", ".join(str(c) for c in obj.cursus.all()) or "Toutes séries"

    @admin.action(description="Compiler le contenu depuis les sections")
    def compiler_depuis_sections(self, request, queryset):
        for cours in queryset:
            cours.compile_from_sections()
        self.message_user(request, f"{queryset.count()} cours compilé(s).")
