"""
Les passages d'un contenu à l'autre que la navigation n'offrait pas (audit du 2026-11-25) : d'un cours vers les épreuves où
la notion est tombée, et d'une épreuve vers les quiz de ses thèmes. Les données étaient déjà reliées par les thèmes.

Publics comme les pages qui les montrent : ils ne donnent que des titres, des années et des noms de thèmes, jamais un
énoncé ni un corrigé. L'accès au contenu reste décidé par la page de destination.
"""

from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from quiz.models import CompetenceItem

from .models import Cours, Lesson, Origine, Question, StatutContenu

EPREUVES_CITEES_MAX = 6
THEMES_CITES_MAX = 6


def _cursus_demande(request):
    valeur = request.query_params.get("cursus", "")
    return int(valeur) if valeur.isdigit() else None


class CoursOuTombeView(APIView):
    """
    GET cours/<slug>/epreuves/?cursus= : les épreuves OFFICIELLES de la matière du cours qui portent l'un de ses thèmes.
    `cursus` restreint à l'examen de l'élève ; sans lui, aux examens du cours s'il en a. {total, annees, epreuves}.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, slug):
        cours = get_object_or_404(Cours.objects.visibles().par_slug_ou_id(slug))
        themes = list(cours.tags.values_list("pk", flat=True))
        vide = {"total": 0, "annees": [], "epreuves": []}
        if not themes:
            return Response(vide)
        cursus = _cursus_demande(request)
        examens_du_cours = list(cours.cursus.values_list("pk", flat=True))
        questions = Question.objects.filter(
            themes__in=themes, exercise__statut=StatutContenu.VALIDE, exercise__lesson__statut=StatutContenu.VALIDE,
            exercise__lesson__subject_id=cours.subject_id, exercise__lesson__origine=Origine.OFFICIEL,
        )
        if cursus is not None:
            questions = questions.filter(exercise__lesson__cursus=cursus)
        elif examens_du_cours:
            questions = questions.filter(exercise__lesson__cursus__in=examens_du_cours)
        ids = set(questions.values_list("exercise__lesson_id", flat=True))
        if not ids:
            return Response(vide)
        epreuves = list(
            Lesson.objects.filter(pk__in=ids).order_by("-year", "title").values("slug", "title", "year")
        )
        annees = sorted({e["year"] for e in epreuves if e["year"]}, reverse=True)
        return Response({"total": len(epreuves), "annees": annees, "epreuves": epreuves[:EPREUVES_CITEES_MAX]})


class EpreuveThemesQuizView(APIView):
    """
    GET lessons/<slug>/quiz/?cursus= : les thèmes de cette épreuve qui ont des questions de quiz pour l'examen demandé
    (à défaut le premier de l'épreuve), les plus présents dans l'épreuve d'abord. {cursus_id, themes}.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, slug):
        lesson = get_object_or_404(Lesson.objects.visibles().par_slug_ou_id(slug))
        examens = list(lesson.cursus.values_list("pk", flat=True).order_by("pk"))
        demande = _cursus_demande(request)
        cursus = demande if demande in examens else (examens[0] if examens else None)
        if cursus is None:
            return Response({"cursus_id": None, "themes": []})
        presents = (
            Question.themes.through.objects.filter(question__exercise__lesson=lesson, question__exercise__statut=StatutContenu.VALIDE)
            .values("tag_id", "tag__name").annotate(nb=Count("question_id")).order_by("-nb", "tag__name")
        )
        presents = list(presents)
        avec_quiz = dict(
            CompetenceItem.objects.filter(
                theme_id__in=[p["tag_id"] for p in presents], cursus=cursus, subject_id=lesson.subject_id,
                statut=StatutContenu.VALIDE,
            ).values_list("theme_id").annotate(nb=Count("pk"))
        )
        themes = [
            {"theme_id": p["tag_id"], "theme": p["tag__name"], "questions_quiz": avec_quiz[p["tag_id"]]}
            for p in presents if p["tag_id"] in avec_quiz
        ]
        return Response({"cursus_id": cursus, "themes": themes[:THEMES_CITES_MAX]})
