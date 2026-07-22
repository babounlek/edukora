from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from catalog.models import Cours, Lesson, StatutContenu
from catalog.serializers import CoursSerializer, LessonSerializer

from .models import LectureProgress
from .services import has_access


@api_view(["GET"])
def read_lesson(request, lesson_id):
    """Contenu pour lecture en ligne (Markdown), réservé aux abonnés."""
    lesson = get_object_or_404(Lesson, pk=lesson_id, statut=StatutContenu.VALIDE)

    if not has_access(request.user, lesson):
        return Response({"error": "Abonnement requis pour lire ce contenu."}, status=403)

    LectureProgress.objects.update_or_create(user=request.user, lesson=lesson)

    return Response({
        "id": lesson.id,
        "title": lesson.title,
        "content_markdown": lesson.content_markdown,
        "header": lesson.header_info(),
        "sujet_pdf_url": request.build_absolute_uri(lesson.sujet_pdf.url) if lesson.sujet_pdf else None,
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def preview_lesson(request, lesson_id):
    """Sujet public (tout le monde, abonné ou non) : tous les énoncés, jamais le corrigé."""
    lesson = get_object_or_404(Lesson, pk=lesson_id, statut=StatutContenu.VALIDE)

    return Response({
        "id": lesson.id,
        "title": lesson.title,
        "preview_markdown": lesson.preview_markdown(),
        "header": lesson.header_info(),
    })


@api_view(["GET"])
def read_cours(request, cours_id):
    """Contenu pour lecture en ligne (Markdown), réservé aux abonnés."""
    cours = get_object_or_404(Cours, pk=cours_id, statut=StatutContenu.VALIDE)

    if not has_access(request.user, cours):
        return Response({"error": "Abonnement requis pour lire ce contenu."}, status=403)

    LectureProgress.objects.update_or_create(user=request.user, cours=cours)

    return Response({
        "id": cours.id,
        "title": cours.titre,
        "content_markdown": cours.content_markdown,
        "header": cours.header_info(),
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def preview_cours(request, cours_id):
    """Aperçu public (non-abonné) : accroche + prérequis + règle seulement."""
    cours = get_object_or_404(Cours, pk=cours_id, statut=StatutContenu.VALIDE)

    return Response({
        "id": cours.id,
        "title": cours.titre,
        "preview_markdown": cours.preview_markdown(),
        "header": cours.header_info(),
    })


@api_view(["GET"])
def my_progression(request):
    """Leçons et cours dont l'utilisateur a ouvert la lecture complète, du plus récent au plus ancien."""
    lessons = (
        Lesson.objects.filter(lectures__user=request.user, statut=StatutContenu.VALIDE)
        .order_by("-lectures__last_read_at")
    )
    cours = (
        Cours.objects.filter(lectures__user=request.user, statut=StatutContenu.VALIDE)
        .order_by("-lectures__last_read_at")
    )

    return Response({
        "lessons": LessonSerializer(lessons, many=True, context={"request": request}).data,
        "cours": CoursSerializer(cours, many=True, context={"request": request}).data,
    })
