from django.db.models import Q
from rest_framework import generics, permissions

from .models import Cours, Cursus, Lesson, StatutContenu, Subject
from .serializers import CoursSerializer, CursusSerializer, LessonSerializer, SubjectSerializer


class LessonListView(generics.ListAPIView):
    serializer_class = LessonSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = (
            Lesson.objects.filter(statut=StatutContenu.VALIDE)
            .select_related("subject")
            .prefetch_related("cursus__series", "themes")
        )

        params = self.request.query_params
        if subject := params.get("subject"):
            qs = qs.filter(subject__code=subject)
        if cursus_id := params.get("cursus"):
            qs = qs.filter(cursus__id=cursus_id)
        if lesson_type := params.get("lesson_type"):
            qs = qs.filter(lesson_type=lesson_type)
        if origine := params.get("origine"):
            qs = qs.filter(origine=origine)
        if search := params.get("search"):
            # Plein texte : titre, contenu compilé, thèmes et mots-clés - pas seulement
            # le titre, pour qu'une recherche par notion ("discriminant") trouve les
            # corrigés qui la traitent même si elle n'apparaît pas dans le titre.
            qs = qs.filter(
                Q(title__icontains=search)
                | Q(content_markdown__icontains=search)
                | Q(themes__name__icontains=search)
                | Q(mots_cles_recherche__name__icontains=search),
            )

        return qs.distinct()


class LessonDetailView(generics.RetrieveAPIView):
    serializer_class = LessonSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Lesson.objects.filter(statut=StatutContenu.VALIDE).select_related(
        "subject",
    ).prefetch_related("cursus__series")


class CoursListView(generics.ListAPIView):
    serializer_class = CoursSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = (
            Cours.objects.filter(statut=StatutContenu.VALIDE)
            .select_related("subject")
            .prefetch_related("cursus__series", "tags")
        )

        params = self.request.query_params
        if subject := params.get("subject"):
            qs = qs.filter(subject__code=subject)
        if cursus_id := params.get("cursus"):
            qs = qs.filter(cursus__id=cursus_id)
        if search := params.get("search"):
            qs = qs.filter(
                Q(titre__icontains=search)
                | Q(content_markdown__icontains=search)
                | Q(tags__name__icontains=search),
            )

        return qs.distinct()


class CoursDetailView(generics.RetrieveAPIView):
    serializer_class = CoursSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Cours.objects.filter(statut=StatutContenu.VALIDE).select_related(
        "subject",
    ).prefetch_related("cursus__series", "tags")


class SubjectListView(generics.ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class CursusListView(generics.ListAPIView):
    queryset = Cursus.objects.select_related("series").all()
    serializer_class = CursusSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
