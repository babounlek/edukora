"""
Rappels de méthode des épreuves GCE O Level, et cours ouverts par les épreuves gratuites.

Les corrigés GCE ont été rédigés à l'ingestion, sans bloc « Rappel de méthode » ni RappelDeMethode : rien
ne reliait donc une épreuve aux cours de ses thèmes (les cours, eux, existent un par thème). Cette commande
comble le manque :

  - Paper 2 (réponses rédigées en plusieurs parties, où une méthode aide le plus) : par exercice, pour les 2
    thèmes qui reviennent le plus parmi ses questions (et qui ont un cours publié), elle écrit en tête du
    corrigé de la première question de ce thème un bloc « ### Rappel de méthode » tiré du cours (ses 3
    premiers points à retenir : une règle générale, jamais une réponse) et crée le RappelDeMethode
    correspondant, relié au cours. Le lecteur en tire le bouton « Voir le cours complet » ;
  - Paper 1 (50 QCM) payant : pas de rappels, il passe par les liens de cours par THÈME sous chaque question
    (voir catalog.rendering._ajouter_liens_cours_par_theme) ;
  - épreuve GRATUITE (Lesson.est_vitrine), quel que soit son paper : chaque cours que le lecteur propose sous
    une question de l'épreuve reçoit un rappel qui y mène, écrit sous la première question qui le cite, pour
    que l'échantillon gratuit montre tous ses rappels de méthode. Les rappels déjà créés sans cours sont
    reliés. (Depuis le 2026-10-14 tout cours est libre en lecture : ce n'est plus ce qui ouvre un cours, voir
    access.services.has_access ; seuls ses exercices d'application restent payants.)

Idempotente (clé : external_id du rappel, et « ce cours a déjà un rappel dans cette épreuve ») et rejouable en
production, APRÈS l'ingestion des épreuves et des cours : les JSON source des épreuves ne portent pas ces rappels.

    python manage.py ajouter_rappels_gce                 # simulation (annulée), affiche le résultat
    python manage.py ajouter_rappels_gce --appliquer     # écrit les rappels et recompile les épreuves
"""
from collections import Counter

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from catalog.models import Cours, Examen, Lesson, RappelDeMethode, StatutContenu, Tag, TypeReponse
from catalog.rendering import _MAX_COURS_PAR_QUESTION, themes_par_specificite

# Matières GCE qui ont des cours (la Biologie n'en a pas).
MATIERES_AVEC_COURS = ("GCE_MATHS", "GCE_CHEMISTRY", "GCE_PHYSICS")
RAPPELS_PAR_EXERCICE = 2
POINTS_PAR_RAPPEL = 3


def _paragraphe_de_methode(cours):
    """Les premiers points à retenir du cours, en UN paragraphe (le bloc « Rappel de méthode » s'arrête à la première ligne blanche)."""
    points = []
    for section in cours.sections_raw or []:
        if section.get("type") == "synthese":
            points = [" ".join(str(p).split()) for p in section.get("items_markdown") or [] if str(p).strip()]
    return " ".join(points[:POINTS_PAR_RAPPEL])


class Command(BaseCommand):
    help = "Écrit les rappels de méthode GCE et ouvre les cours cités par les épreuves gratuites - voir la docstring du module."

    def add_arguments(self, parser):
        parser.add_argument("--appliquer", action="store_true", help="Écrire (sinon : simulation annulée).")

    @transaction.atomic
    def handle(self, *args, **options):
        self.compteurs = Counter()
        lessons = (
            Lesson.objects.filter(
                cursus__examen=Examen.GCE_OL, statut=StatutContenu.VALIDE, subject__code__in=MATIERES_AVEC_COURS,
            ).select_related("subject").distinct().order_by("id")
        )
        for lesson in lessons:
            touche = False
            if lesson.numero_paper == 2:
                touche = self._paper_2(lesson)
            if lesson.est_vitrine:
                touche = self._relier_rappels_sans_cours(lesson) or touche
                touche = self._couvrir_cours_cites(lesson) or touche
            if touche:
                for exercise in lesson.exercises.filter(statut=StatutContenu.VALIDE):
                    exercise.compile_from_questions()
                lesson.compile_from_exercises()
                self.compteurs["épreuves recompilées"] += 1

        for libelle, n in self.compteurs.items():
            self.stdout.write(f"{libelle} : {n}")
        total = RappelDeMethode.objects.filter(external_id__startswith="rdm-gce-").count()
        libres = Counter(
            c.subject.code for c in Cours.objects.filter(subject__code__in=MATIERES_AVEC_COURS, statut=StatutContenu.VALIDE)
            .select_related("subject") if c.est_vitrine
        )
        self.stdout.write(self.style.SUCCESS(
            f"{total} rappels GCE au total ; cours GCE gratuits : {sum(libres.values())} {dict(sorted(libres.items()))}",
        ))
        if not options["appliquer"]:
            transaction.set_rollback(True)
            self.stdout.write("(simulation : rien n'a été écrit)")

    def _paper_2(self, lesson):
        touche = False
        for exercise in lesson.exercises.filter(statut=StatutContenu.VALIDE).order_by("id"):
            questions = list(exercise.questions.prefetch_related("themes").order_by("ordre"))
            cours_du_theme, ordre = themes_par_specificite(lesson, questions)
            if not cours_du_theme:
                continue
            # Le thème d'une question = son thème le plus SPÉCIFIQUE qui a un cours (même règle que les
            # liens du lecteur) : le rappel d'un thème large traiterait d'autre chose que la question.
            frequence, premiere = Counter(), {}
            for q, themes in zip(questions, ordre):
                if themes:
                    frequence[themes[0]] += 1
                    premiere.setdefault(themes[0], q)
            retenus = sorted(frequence, key=lambda pk: (-frequence[pk], questions.index(premiere[pk]), pk))[:RAPPELS_PAR_EXERCICE]
            for theme_pk in retenus:
                theme = next(t for t in premiere[theme_pk].themes.all() if t.pk == theme_pk)
                touche = self._creer_rappel(lesson, exercise, premiere[theme_pk], theme, cours_du_theme[theme_pk]) or touche
        return touche

    def _relier_rappels_sans_cours(self, lesson):
        """Épreuve gratuite : un rappel GCE créé quand seul un cours par matière restait relié retrouve le cours de son thème."""
        touche = False
        for rappel in RappelDeMethode.objects.filter(
            exercise__lesson=lesson, external_id__startswith="rdm-gce-", cours__isnull=True,
        ):
            theme = Tag.objects.filter(name=rappel.competence).first()
            cours = cours_par_theme(lesson, theme)
            if cours is not None:
                rappel.cours = cours
                rappel.save(update_fields=["cours"])
                self.compteurs["rappels reliés a posteriori"] += 1
                touche = True
        return touche

    def _couvrir_cours_cites(self, lesson):
        """Épreuve gratuite : un rappel pour chaque cours que le lecteur propose sous une question et qu'aucun rappel ne relie encore."""
        touche = False
        deja = set()
        for exercise in lesson.exercises.filter(statut=StatutContenu.VALIDE).order_by("id"):
            questions = list(exercise.questions.prefetch_related("themes").order_by("ordre"))
            cours_du_theme, ordre = themes_par_specificite(lesson, questions)
            for question, themes in zip(questions, ordre):
                plafond = 1 if question.type_reponse == TypeReponse.QCM else _MAX_COURS_PAR_QUESTION
                for theme_pk in themes[:plafond]:
                    cours = cours_du_theme[theme_pk]
                    if cours.pk in deja:
                        continue
                    deja.add(cours.pk)
                    if RappelDeMethode.objects.filter(exercise__lesson=lesson, cours=cours).exists():
                        continue
                    theme = next(t for t in question.themes.all() if t.pk == theme_pk)
                    touche = self._creer_rappel(lesson, exercise, question, theme, cours) or touche
        return touche

    def _creer_rappel(self, lesson, exercise, question, theme, cours):
        external_id = f"rdm-gce-{lesson.slug}-ex{slugify(exercise.numero_exercice)}-{slugify(theme.name)}-0"
        if RappelDeMethode.objects.filter(external_id=external_id).exists():
            return False
        paragraphe = _paragraphe_de_methode(cours)
        if not paragraphe:
            self.stderr.write(f"Cours sans points à retenir : {cours.titre}")
            return False
        # Le rappel ouvre le corrigé de la question en cours de traitement : on relit la ligne, un autre rappel
        # a pu s'y ajouter depuis le chargement de la liste.
        question.refresh_from_db(fields=["corrige_markdown"])
        question.corrige_markdown = f"### Rappel de méthode\n\n{paragraphe}\n\n{question.corrige_markdown}"
        question.save(update_fields=["corrige_markdown"])
        RappelDeMethode.objects.create(
            exercise=exercise, external_id=external_id, competence=theme.name,
            contenu_markdown=paragraphe, cours=cours,
        )
        self.compteurs["rappels créés"] += 1
        return True


def cours_par_theme(lesson, theme):
    """Le cours publié du Tag `theme` pour cette épreuve (voir catalog.rendering.cours_publies_par_theme), ou None."""
    from catalog.rendering import cours_publies_par_theme

    if theme is None:
        return None
    return cours_publies_par_theme(lesson, {theme.pk}).get(theme.pk)
