from django.db.models import Q
from rest_framework import generics, permissions

from .models import Cours, Country, Cursus, Lesson, StatutContenu, Subject
from .serializers import CoursSerializer, CountrySerializer, CursusSerializer, LessonSerializer, SubjectSerializer


class LessonListView(generics.ListAPIView):
    serializer_class = LessonSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = (
            Lesson.objects.filter(statut=StatutContenu.VALIDE)
            .select_related("subject")
            .prefetch_related("cursus__series", "cursus__country", "themes")
        )

        params = self.request.query_params
        if subject := params.get("subject"):
            qs = qs.filter(subject__code=subject)
        if cursus_id := params.get("cursus"):
            qs = qs.filter(cursus__id=cursus_id)
        if country := params.get("country"):
            qs = qs.filter(cursus__country__code__iexact=country)
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
    ).prefetch_related("cursus__series", "cursus__country")


class CoursListView(generics.ListAPIView):
    serializer_class = CoursSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = (
            Cours.objects.filter(statut=StatutContenu.VALIDE)
            .select_related("subject")
            .prefetch_related("cursus__series", "cursus__country", "tags")
        )

        params = self.request.query_params
        if subject := params.get("subject"):
            qs = qs.filter(subject__code=subject)
        if cursus_id := params.get("cursus"):
            qs = qs.filter(cursus__id=cursus_id)
        if country := params.get("country"):
            # cursus vide = notion commune à toutes les séries de tout pays (voir
            # Cours.cursus) - exclue par erreur si on filtrait juste sur cursus__country.
            qs = qs.filter(Q(cursus__isnull=True) | Q(cursus__country__code__iexact=country))
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
    ).prefetch_related("cursus__series", "cursus__country", "tags")


class SubjectListView(generics.ListAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        qs = Subject.objects.all()
        if country := self.request.query_params.get("country"):
            qs = qs.filter(country__code__iexact=country)
        return qs


class CountryListView(generics.ListAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class CursusListView(generics.ListAPIView):
    serializer_class = CursusSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        qs = Cursus.objects.select_related("series", "country").all()
        if country := self.request.query_params.get("country"):
            qs = qs.filter(country__code__iexact=country)
        return qs
