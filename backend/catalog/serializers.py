from rest_framework import serializers

from access.services import has_access

from .models import Cours, Country, Cursus, Lesson, Series, StatutContenu, Subject, Tag, Temoignage


class CountrySerializer(serializers.ModelSerializer):
    # Un Country peut exister en base (référentiel Subject/Series/Cursus) avant que du
    # contenu réel n'y soit ingéré - le sélecteur de pays parcouru (CountrySwitcher) ne
    # doit proposer que les pays où il y a effectivement quelque chose à lire, pas
    # laisser un visiteur atterrir sur un catalogue vide.
    has_lessons = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = ["id", "code", "label", "dial_code", "currency", "has_lessons"]

    def get_has_lessons(self, obj):
        return obj.subjects.filter(lessons__statut=StatutContenu.VALIDE).exists()


class SeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Series
        fields = ["id", "code", "label"]


class SubjectSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)

    class Meta:
        model = Subject
        fields = ["id", "code", "label", "country"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class TemoignageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Temoignage
        fields = ["id", "auteur_nom", "auteur_description", "contenu", "note"]


class CursusSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)
    series = SeriesSerializer(read_only=True)
    # display_examen() plutôt que get_examen_display() : le nom affiché peut être
    # différent du libellé générique selon le pays (ex: BFEM au Sénégal) - voir
    # ExamenLabel dans catalog.models.
    examen_display = serializers.SerializerMethodField()

    class Meta:
        model = Cursus
        fields = ["id", "country", "examen", "examen_display", "series"]

    def get_examen_display(self, obj):
        return obj.display_examen()


class _HasAccessMixin:
    """Résout has_access/is_read depuis l'utilisateur de la requête, partagé par Lesson et Cours."""

    def _current_user(self):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        return user if user and user.is_authenticated else None

    def get_has_access(self, obj):
        # Une Lesson vitrine (voir has_access) est lisible par un visiteur anonyme -
        # court-circuite _current_user() ici même, qui renvoie toujours None pour lui
        # et masquerait sinon ce cas particulier.
        if getattr(obj, "est_vitrine", False):
            return True
        user = self._current_user()
        return bool(user and has_access(user, obj))

    def get_is_read(self, obj):
        user = self._current_user()
        return bool(user and obj.lectures.filter(user=user).exists())


def _cours_content_summary(sections_raw):
    """
    Signal léger sur le contenu d'un Cours, dérivé directement de sections_raw (pas du
    rendu complet, voir Cours.sections_breakdown) - pour un indicateur rapide sur une
    carte/fiche avant ouverture (ex. CoursCard), sans requête ni construction
    supplémentaire.
    """
    has_exemple_resolu = False
    exercices_count = 0
    for section in sections_raw:
        section_type = section.get("type")
        if section_type == "exemple_resolu":
            has_exemple_resolu = True
        elif section_type == "exercices_application":
            exercices_count += len(section.get("items") or [])
    return {"has_exemple_resolu": has_exemple_resolu, "exercices_count": exercices_count}


class CoursSummarySerializer(_HasAccessMixin, serializers.ModelSerializer):
    """Version allégée de Cours pour l'affichage "Cours associés" sur une Lesson."""

    has_access = serializers.SerializerMethodField()
    apercu_contenu = serializers.SerializerMethodField()

    class Meta:
        model = Cours
        fields = ["id", "slug", "titre", "has_access", "apercu_contenu"]

    def get_apercu_contenu(self, obj):
        return _cours_content_summary(obj.sections_raw)


class LessonSerializer(_HasAccessMixin, serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    cursus = CursusSerializer(read_only=True, many=True)
    lesson_type_display = serializers.CharField(source="get_lesson_type_display", read_only=True)
    origine_display = serializers.CharField(source="get_origine_display", read_only=True)
    nature_epreuve_display = serializers.CharField(source="get_nature_epreuve_display", read_only=True)
    themes = TagSerializer(many=True, read_only=True)
    has_access = serializers.SerializerMethodField()
    is_read = serializers.SerializerMethodField()
    exercises_count = serializers.SerializerMethodField()
    related_cours = serializers.SerializerMethodField()
    sujet_pdf_url = serializers.SerializerMethodField()
    kind = serializers.SerializerMethodField()
    duree_minutes = serializers.SerializerMethodField()
    sujet_pdf_disponible = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            "id", "kind", "slug", "title", "subject", "cursus", "lesson_type", "lesson_type_display",
            "year", "duree_epreuve", "duree_minutes", "coefficient", "origine", "origine_display",
            "etablissement", "nature_epreuve", "nature_epreuve_display", "themes",
            "has_access", "is_read", "est_vitrine", "created_at",
            "exercises_count", "related_cours", "sujet_pdf_url", "sujet_pdf_disponible",
        ]

    def get_kind(self, obj):
        return "classique"

    def get_duree_minutes(self, obj):
        # Toujours null côté Lesson - existe pour que le frontend ait un seul champ,
        # jamais présent seulement côté EpreuveInedite (voir catalog.inedit_bridge).
        return None

    def get_sujet_pdf_disponible(self, obj):
        # Toujours False côté Lesson - le sujet classique est déjà exposé via
        # sujet_pdf_url (URL publique directe) : ce booléen n'a de sens que côté
        # EpreuveInedite, dont le sujet reste un contenu payant (voir
        # catalog.inedit_bridge et inedit.views.download_sujet_pdf, gated).
        return False

    def get_exercises_count(self, obj):
        return obj.exercises.filter(statut=StatutContenu.VALIDE).count()

    def get_sujet_pdf_url(self, obj):
        # Généré hors ligne (voir catalog/sujet_pdf.py) : null tant que la commande/
        # action admin ne l'a pas encore produit, jamais généré à la demande ici.
        if not obj.sujet_pdf:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.sujet_pdf.url) if request else obj.sujet_pdf.url

    def get_related_cours(self, obj):
        cours_qs = Cours.objects.filter(
            rappels_source__exercise__lesson=obj, statut=StatutContenu.VALIDE,
        ).distinct()
        return CoursSummarySerializer(cours_qs, many=True, context=self.context).data


class CoursSerializer(_HasAccessMixin, serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    cursus = CursusSerializer(read_only=True, many=True)
    tags = TagSerializer(many=True, read_only=True)
    has_access = serializers.SerializerMethodField()
    is_read = serializers.SerializerMethodField()
    apercu_contenu = serializers.SerializerMethodField()

    class Meta:
        model = Cours
        fields = [
            "id", "slug", "titre", "subject", "cursus", "sous_theme",
            "duree_estimee_min", "tags", "has_access", "is_read", "apercu_contenu", "created_at",
        ]

    def get_apercu_contenu(self, obj):
        return _cours_content_summary(obj.sections_raw)
