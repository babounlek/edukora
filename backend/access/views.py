from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from catalog.models import Cours, Exercise, Lesson

from .models import ExerciceFait, LectureProgress
from .services import has_access


class _LessonProgressionSerializer(serializers.ModelSerializer):
    """Version minimale de catalog.serializers.LessonSerializer, pour my_progression
    ci-dessous seulement - cet endpoint liste TOUT l'historique de lecture d'un
    utilisateur (potentiellement des centaines de lignes), sans aucune pagination. Le
    frontend n'y lit que id/slug/title/subject.country.code (voir "Reprendre ma
    lecture" sur CataloguePage.tsx/CoursListPage.tsx et "Ma progression" sur
    AccountPage.tsx) : le serializer complet y réintroduirait, sans borne de page cette
    fois, le même coût par ligne (exercises_count, related_cours, Cours.est_vitrine...)
    déjà corrigé côté catalogue (voir catalog.views.LessonListView/CoursListView)."""

    subject = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ["id", "slug", "title", "subject"]

    def get_subject(self, obj):
        return {"country": {"code": obj.subject.country.code}}


class _CoursProgressionSerializer(serializers.ModelSerializer):
    """Miroir de _LessonProgressionSerializer ci-dessus, même raison."""

    class Meta:
        model = Cours
        fields = ["id", "slug", "titre"]


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

    # Exercices de CETTE épreuve que le lecteur a déjà déclaré avoir traités - une
    # seule requête pour toute la page. Sert à proposer la validation au bon endroit,
    # à la fin du corrigé (voir access.ExerciceFait) : c'est le seul moment où l'élève
    # a réellement de quoi juger s'il a résolu l'exercice.
    exercices_faits = set()
    if request.user.is_authenticated:
        exercices_faits = set(
            ExerciceFait.objects.filter(user=request.user, exercise__lesson=lesson)
            .values_list("exercise_id", flat=True),
        )
    exercices = [dict(e, fait=e.get("id") in exercices_faits) for e in lesson.exercises_breakdown()]

    return Response({
        "id": lesson.id,
        "title": lesson.title,
        "content_markdown": lesson.content_markdown,
        # Consigne(s) valables pour l'épreuve entière (voir Lesson.introduction_markdown) -
        # exposée à part, jamais dans `exercises` : elle ne concerne aucun exercice en
        # particulier, un lecteur qui saute directement à l'exercice 3 ne doit pas la
        # revoir. Le frontend l'affiche une seule fois, avant le sommaire/premier exercice.
        "introduction_markdown": lesson.introduction_markdown,
        # Énoncé/corrigé par exercice, séparément - voir Lesson.exercises_breakdown.
        # Liste vide pour une Lesson sans Exercise (FICHE...) : le frontend retombe
        # alors sur content_markdown tel quel plutôt que de replier un énoncé qu'on
        # n'a pas isolé.
        "exercises": exercices,
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
        # Voir la même clé sur read_lesson ci-dessus - le sujet public montre les
        # consignes d'épreuve au même titre que les énoncés, jamais le corrigé.
        "introduction_markdown": lesson.introduction_markdown,
        # Le même sujet, découpé par exercice, pour que la fiche puisse renvoyer
        # directement vers le corrigé de l'exercice lu (/lire#exercice-3) - voir
        # Lesson.preview_exercises, qui n'expose aucun champ de corrigé. Liste vide
        # pour une Lesson sans Exercise : le frontend retombe sur preview_markdown.
        "exercises": lesson.preview_exercises(),
        "header": lesson.header_info(),
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def read_cours(request, cours_id):
    """
    Contenu pour lecture en ligne (Markdown) - réservé aux abonnés, sauf un Cours
    "vitrine" (voir Cours.est_vitrine, dérivé de sa/ses épreuve(s) source(s)), lisible
    par un visiteur anonyme : AllowAny ici, has_access() ci-dessous fait le vrai tri
    au cas par cas - même patron que read_lesson.
    """
    qs = Cours.objects.visibles().select_related("subject__country").par_slug_ou_id(cours_id)
    cours = get_object_or_404(qs)

    if not has_access(request.user, cours):
        return Response({"error": "Abonnement requis pour lire ce contenu."}, status=403)

    if request.user.is_authenticated:
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
        .select_related("subject__country")
        .order_by("-lectures__last_read_at")
    )
    cours = (
        Cours.objects.visibles().filter(lectures__user=request.user)
        .order_by("-lectures__last_read_at")
    )

    return Response({
        "lessons": _LessonProgressionSerializer(lessons, many=True).data,
        "cours": _CoursProgressionSerializer(cours, many=True).data,
    })


@api_view(["POST"])
def marquer_exercice_fait(request, exercise_id):
    """
    L'élève déclare avoir traité cet exercice - ou revient sur sa déclaration.

    Toujours explicite : rien ici n'est déduit d'une ouverture de page (voir
    ExerciceFait). `fait` absent vaut true, pour que le cas courant tienne en un POST
    sans corps.

    Réservé à qui a accès à l'épreuve : marquer comme fait un exercice qu'on ne peut
    pas lire n'a aucun sens, et gonflerait un compteur de progression sans travail
    derrière.
    """
    exercise = get_object_or_404(Exercise.objects.select_related("lesson"), pk=exercise_id)
    if not has_access(request.user, exercise.lesson):
        return Response({"error": "Abonnement requis pour cette épreuve."}, status=403)

    fait = request.data.get("fait", True)
    if fait:
        ExerciceFait.objects.get_or_create(user=request.user, exercise=exercise)
    else:
        ExerciceFait.objects.filter(user=request.user, exercise=exercise).delete()
    return Response({"exercise_id": exercise.pk, "fait": bool(fait)})
