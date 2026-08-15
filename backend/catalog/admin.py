import json
from pathlib import Path

from django.conf import settings
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.shortcuts import redirect, render
from django.urls import path

from .ingestion import IngestionError, ingest_exercise, queue_ingestion, read_ingestion_report
from .models import Cours, Country, Cursus, ExamenLabel, ExamSession, Exercise, Figure, Lesson, Question, RappelDeMethode, Series, Subject, Tag, Temoignage
from .sujet_pdf import queue_sujet_pdf_generation

# Phrase à taper pour confirmer la purge (voir LessonAdmin.purge_view) - une action qui
# efface tout le contenu ne doit jamais être déclenchable par un simple clic accidentel.
PURGE_CONFIRMATION_PHRASE = "SUPPRIMER TOUT"

# Dossier surveillé par la tâche planifiée qui dépose les JSON produits par la
# compétence correction-experte - voir catalog.ingestion.run_ingestion.
INGEST_DIR = Path(settings.BASE_DIR) / "ingest"


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ["code", "label", "dial_code", "currency", "actif"]
    list_filter = ["actif"]
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


@admin.register(ExamenLabel)
class ExamenLabelAdmin(admin.ModelAdmin):
    list_display = ["country", "examen", "label"]
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


@admin.register(Temoignage)
class TemoignageAdmin(admin.ModelAdmin):
    list_display = ["auteur_nom", "auteur_description", "note", "est_publie", "created_at"]
    list_filter = ["est_publie", "note"]
    list_editable = ["est_publie"]
    search_fields = ["auteur_nom", "contenu"]


class ExerciseInline(admin.TabularInline):
    model = Exercise
    extra = 0
    fields = ["numero_exercice", "points", "statut"]
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
    list_display = ["title", "subject", "nature_epreuve", "cursus_list", "lesson_type", "origine", "year", "statut", "est_vitrine", "updated_at"]
    list_filter = ["statut", "lesson_type", "origine", "subject", "nature_epreuve", "cursus", "est_vitrine"]
    list_editable = ["est_vitrine"]
    search_fields = ["title", "epreuve_source", "slug"]
    filter_horizontal = ["cursus", "themes", "mots_cles_recherche"]
    inlines = [ExerciseInline]
    actions = ["compiler_depuis_exercices", "generer_pdf_sujet"]
    # Auto-rempli en JS depuis le titre (comportement natif de l'admin) - reste
    # modifiable manuellement si besoin avant la première sauvegarde ; Lesson.save()
    # ne régénère jamais un slug déjà renseigné (voir generate_unique_slug).
    prepopulated_fields = {"slug": ("title",)}

    def get_urls(self):
        custom_urls = [
            path("ingestion/", self.admin_site.admin_view(self.ingestion_view), name="catalog_lesson_ingestion"),
            path("purger/", self.admin_site.admin_view(self.purge_view), name="catalog_lesson_purge"),
        ]
        return custom_urls + super().get_urls()

    def ingestion_view(self, request):
        """
        Lance `manage.py ingest_corrections` sur INGEST_DIR - le pendant, depuis l'admin,
        de la même commande en ligne de commande : évite d'avoir à ouvrir un terminal pour
        injecter les fichiers déposés par correction-experte.

        Le run part dans un processus détaché, jamais dans ce thread de requête : il dure
        largement plus que le `--timeout 30` de gunicorn dès que le dossier grossit, et le
        worker se faisait tuer en plein run (voir catalog.ingestion.queue_ingestion). La
        page n'affiche donc plus le rapport dans sa réponse au clic, mais celui du dernier
        run, relu sur disque à chaque affichage - et les PDF de sujet manquants sont
        générés par la commande elle-même, plus par cette vue.
        """
        report = read_ingestion_report()
        if request.method == "POST":
            if report and report.get("status") == "running":
                messages.warning(
                    request,
                    "Une ingestion est déjà en cours - attendez qu'elle se termine avant "
                    "d'en relancer une (actualisez cette page pour suivre son état).",
                )
            else:
                queue_ingestion(INGEST_DIR)
                messages.info(
                    request,
                    "Ingestion lancée en arrière-plan. Actualisez cette page pour suivre "
                    "son avancement : le rapport s'affichera ici une fois le run terminé.",
                )
            # POST/redirect/GET : sans ça, actualiser la page pour justement suivre le run
            # en cours reproposerait d'en lancer un second.
            return redirect(request.path)

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


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ["numero", "ordre", "difficulte_estimee", "type_reponse", "reponse_correcte"]
    show_change_link = True


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ["lesson", "numero_exercice", "statut", "updated_at"]
    list_filter = ["statut"]
    search_fields = ["lesson__title", "lesson__epreuve_source", "enonce_markdown"]
    filter_horizontal = ["themes", "mots_cles_recherche"]
    autocomplete_fields = ["lesson"]
    inlines = [QuestionInline, RappelDeMethodeInline, FigureInline]
    actions = ["recompiler_depuis_questions", "reingerer_depuis_fichier"]

    @admin.action(description="Recompiler enonce/corrige/themes depuis les Question")
    def recompiler_depuis_questions(self, request, queryset):
        for exercise in queryset:
            exercise.compile_from_questions()
        self.message_user(request, f"{queryset.count()} exercice(s) recompilé(s).")

    @admin.action(description="Réingérer depuis le fichier JSON source (écrase le contenu actuel)")
    def reingerer_depuis_fichier(self, request, queryset):
        """
        Une épreuve peut avoir été corrigée après sa première ingestion (le fichier
        JSON sous INGEST_DIR a été modifié) - cette action relit ce fichier et
        remplace le contenu de l'Exercise sélectionné (voir ingest_exercise,
        force=True), plutôt que d'être ignorée comme le fait une ingestion normale
        (idempotente par défaut, précisément pour ne jamais écraser une correction
        manuelle faite depuis l'admin sans qu'on l'ait explicitement demandé).

        Le chemin du fichier n'est pas stocké en base - il est reconstruit depuis
        `lesson.epreuve_source` (nom du fichier PDF d'origine) et le code pays du
        sujet, en suivant la convention de nommage de l'ingestion
        (`ingest/<pays>/<epreuve>/<epreuve>_exercice_<numero>.json`). Cette
        convention n'est pas imposée par une contrainte en base : si `epreuve_source`
        a été modifié à la main depuis l'admin sans que le fichier corresponde
        encore, l'action échoue proprement (message d'erreur par exercice) plutôt que
        de deviner un autre chemin.
        """
        reussis = 0
        for exercise in queryset.select_related("lesson__subject__country"):
            lesson = exercise.lesson
            if not lesson.epreuve_source:
                self.message_user(
                    request,
                    f"{exercise} : epreuve_source vide sur la leçon, impossible de retrouver le fichier source.",
                    level=messages.ERROR,
                )
                continue

            nom_epreuve = lesson.epreuve_source.removesuffix(".pdf")
            country_code = lesson.subject.country.code.lower()
            source_dir = INGEST_DIR / country_code / nom_epreuve
            json_path = source_dir / f"{nom_epreuve}_exercice_{exercise.numero_exercice}.json"

            if not json_path.exists():
                self.message_user(
                    request,
                    f"{exercise} : fichier introuvable ({json_path.relative_to(INGEST_DIR)}).",
                    level=messages.ERROR,
                )
                continue

            try:
                data = json.loads(json_path.read_text(encoding="utf-8"))
                ingest_exercise(data, source_dir=source_dir, force=True)
                reussis += 1
            except (IngestionError, OSError, ValueError) as exc:
                self.message_user(request, f"{exercise} : {exc}", level=messages.ERROR)

        if reussis:
            self.message_user(request, f"{reussis} exercice(s) réingéré(s) depuis leur fichier source.")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["exercise", "numero", "difficulte_estimee", "type_reponse"]
    list_filter = ["type_reponse", "difficulte_estimee"]
    search_fields = ["exercise__lesson__title", "enonce_markdown"]
    filter_horizontal = ["themes"]
    autocomplete_fields = ["exercise"]


@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):
    list_display = ["titre", "subject", "cursus_list", "sous_theme", "statut", "updated_at"]
    list_filter = ["statut", "subject", "cursus"]
    search_fields = ["titre", "sous_theme", "external_id"]
    filter_horizontal = ["cursus", "tags"]
    actions = ["compiler_depuis_sections"]
    # Auto-rempli en JS depuis le titre (comportement natif de l'admin) - reste
    # modifiable manuellement si besoin avant la première sauvegarde ; Cours.save() ne
    # régénère jamais un slug déjà renseigné (même logique que LessonAdmin).
    prepopulated_fields = {"slug": ("titre",)}

    @admin.display(description="Cursus")
    def cursus_list(self, obj):
        return ", ".join(str(c) for c in obj.cursus.all()) or "Toutes séries"

    @admin.action(description="Compiler le contenu depuis les sections")
    def compiler_depuis_sections(self, request, queryset):
        for cours in queryset:
            cours.compile_from_sections()
        self.message_user(request, f"{queryset.count()} cours compilé(s).")
