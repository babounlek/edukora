from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions

from .models import Cours, Country, Cursus, Lesson, StatutContenu, Subject
from .serializers import CoursSerializer, CountrySerializer, CursusSerializer, LessonSerializer, SubjectSerializer


class LessonListView(generics.ListAPIView):
    serializer_class = LessonSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = (
            Lesson.objects.visibles()
            .select_related("subject__country")
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
        if params.get("exclude_read") == "true" and self.request.user.is_authenticated:
            # Anonyme : pas de LectureProgress à exclure, donc no-op naturel - on ne
            # teste explicitement is_authenticated que pour éviter un filtre sur
            # lectures__user=AnonymousUser (ne correspond à aucune ligne, mais ambigu).
            qs = qs.exclude(lectures__user=self.request.user)
        if params.get("ordering") == "year":
            # Whitelist explicite plutôt qu'un order_by(params["ordering"]) direct :
            # n'expose que ce que le catalogue propose réellement (années croissantes),
            # jamais un champ arbitraire choisi par le client. -year (défaut, plus
            # récent d'abord) vient déjà de Lesson.Meta.ordering, pas besoin d'un cas ici.
            qs = qs.order_by("year", "title")
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
    queryset = Lesson.objects.visibles().select_related(
        "subject__country",
    ).prefetch_related("cursus__series", "cursus__country")

    def get_object(self):
        qs = self.filter_queryset(self.get_queryset()).par_slug_ou_id(self.kwargs["slug"])
        obj = get_object_or_404(qs)
        self.check_object_permissions(self.request, obj)
        return obj


class CoursListView(generics.ListAPIView):
    serializer_class = CoursSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = (
            Cours.objects.visibles()
            .select_related("subject__country")
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
    queryset = Cours.objects.visibles().select_related(
        "subject__country",
    ).prefetch_related("cursus__series", "cursus__country", "tags")


class SubjectListView(generics.ListAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        # Ne propose que les matières ayant déjà du contenu publié (Épreuve ou Cours) -
        # même principe que CountrySerializer.get_has_lessons, sinon le select liste
        # surtout des matières vides (référentiel Subject bien plus large que le
        # contenu réellement ingéré à date).
        qs = (
            Subject.objects.select_related("country")
            .filter(country__actif=True)
            .filter(Q(lessons__statut=StatutContenu.VALIDE) | Q(cours__statut=StatutContenu.VALIDE))
            .distinct()
        )
        if country := self.request.query_params.get("country"):
            qs = qs.filter(country__code__iexact=country)
        return qs


class CountryListView(generics.ListAPIView):
    queryset = Country.objects.filter(actif=True)
    serializer_class = CountrySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class CursusListView(generics.ListAPIView):
    serializer_class = CursusSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        # Même principe que SubjectListView : un Cursus n'a d'intérêt pour l'élève que
        # s'il porte déjà une Épreuve ou un Cours publié.
        qs = (
            Cursus.objects.select_related("series", "country")
            .filter(country__actif=True)
            .filter(Q(lessons__statut=StatutContenu.VALIDE) | Q(cours__statut=StatutContenu.VALIDE))
            .distinct()
        )
        if country := self.request.query_params.get("country"):
            qs = qs.filter(country__code__iexact=country)
        return qs
