from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from catalog.models import Cours, Lesson
from catalog.serializers import CoursSerializer, LessonSerializer

from .models import LectureProgress
from .services import has_access


@api_view(["GET"])
@permission_classes([AllowAny])
def read_lesson(request, lesson_slug):
    """
    Contenu pour lecture en ligne (Markdown) - réservé aux abonnés, sauf une Lesson
    "vitrine" (voir Lesson.est_vitrine), lisible par un visiteur anonyme : AllowAny ici,
    has_access() ci-dessous fait le vrai tri au cas par cas.
    """
    qs = Lesson.objects.visibles().select_related("subject__country").par_slug_ou_id(lesson_slug)
    lesson = get_object_or_404(qs)

    if not has_access(request.user, lesson):
        return Response({"error": "Abonnement requis pour lire ce contenu."}, status=403)

    if request.user.is_authenticated:
        LectureProgress.objects.update_or_create(user=request.user, lesson=lesson)

    return Response({
        "id": lesson.id,
        "title": lesson.title,
        "content_markdown": lesson.content_markdown,
        # Énoncé/corrigé par exercice, séparément - voir Lesson.exercises_breakdown.
        # Liste vide pour une Lesson sans Exercise (FICHE...) : le frontend retombe
        # alors sur content_markdown tel quel plutôt que de replier un énoncé qu'on
        # n'a pas isolé.
        "exercises": lesson.exercises_breakdown(),
        "header": lesson.header_info(),
        "lesson_type": lesson.lesson_type,
        "sujet_pdf_url": request.build_absolute_uri(lesson.sujet_pdf.url) if lesson.sujet_pdf else None,
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def preview_lesson(request, lesson_slug):
    """Sujet public (tout le monde, abonné ou non) : tous les énoncés, jamais le corrigé."""
    qs = Lesson.objects.visibles().select_related("subject__country").par_slug_ou_id(lesson_slug)
    lesson = get_object_or_404(qs)

    return Response({
        "id": lesson.id,
        "title": lesson.title,
        "preview_markdown": lesson.preview_markdown(),
        # Le même sujet, découpé par exercice, pour que la fiche puisse renvoyer
        # directement vers le corrigé de l'exercice lu (/lire#exercice-3) - voir
        # Lesson.preview_exercises, qui n'expose aucun champ de corrigé. Liste vide
        # pour une Lesson sans Exercise : le frontend retombe sur preview_markdown.
        "exercises": lesson.preview_exercises(),
        "header": lesson.header_info(),
    })


@api_view(["GET"])
def read_cours(request, cours_id):
    """Contenu pour lecture en ligne (Markdown), réservé aux abonnés."""
    qs = Cours.objects.visibles().select_related("subject__country").par_slug_ou_id(cours_id)
    cours = get_object_or_404(qs)

    if not has_access(request.user, cours):
        return Response({"error": "Abonnement requis pour lire ce contenu."}, status=403)

    LectureProgress.objects.update_or_create(user=request.user, cours=cours)

    return Response({
        "id": cours.id,
        "title": cours.titre,
        "content_markdown": cours.content_markdown,
        # Sections individuellement typées, pour un rendu distinguant visuellement
        # chaque type - voir Cours.sections_breakdown(). Liste vide (cas déjà couvert
        # par le fallback frontend, même convention que EpreuveContent.exercises) si
        # sections_raw est vide : le frontend retombe alors sur content_markdown.
        "sections": cours.sections_breakdown(),
        "header": cours.header_info(),
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def preview_cours(request, cours_id):
    """Aperçu public (non-abonné) : accroche + prérequis + règle seulement."""
    qs = Cours.objects.visibles().select_related("subject__country").par_slug_ou_id(cours_id)
    cours = get_object_or_404(qs)

    return Response({
        "id": cours.id,
        "title": cours.titre,
        "preview_markdown": cours.preview_markdown(),
        "sections": cours.sections_breakdown(allowed_types={"accroche", "prerequis", "regle"}),
        "header": cours.header_info(),
    })


@api_view(["GET"])
def my_progression(request):
    """Leçons et cours dont l'utilisateur a ouvert la lecture complète, du plus récent au plus ancien."""
    lessons = (
        Lesson.objects.visibles().filter(lectures__user=request.user)
        .order_by("-lectures__last_read_at")
    )
    cours = (
        Cours.objects.visibles().filter(lectures__user=request.user)
        .order_by("-lectures__last_read_at")
    )

    return Response({
        "lessons": LessonSerializer(lessons, many=True, context={"request": request}).data,
        "cours": CoursSerializer(cours, many=True, context={"request": request}).data,
    })
