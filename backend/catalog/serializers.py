from django.db.models import Count
from rest_framework import serializers

from access.services import has_access

from .models import (
    Cours,
    Country,
    Cursus,
    Exercise,
    Filiere,
    Lesson,
    RappelDeMethode,
    Series,
    StatutContenu,
    Subject,
    Tag,
    Temoignage,
)


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
        # Mémoïsé par pays sur le contexte de sérialisation (partagé par toute
        # l'arborescence de serializers imbriqués d'un même appel many=True, voir
        # DRF Field.context) - CountrySerializer est imbriqué deux fois par Lesson/Cours
        # (subject.country ET cursus[].country), donc sans ce cache une page de 24
        # items relance la même requête .exists() à chaque occurrence du même pays
        # (aujourd'hui un seul pays actif, donc jusqu'à ~50 requêtes identiques par page
        # sans ce correctif - voir l'incident perf sur LessonListView.list).
        cache = self.context.setdefault("_has_lessons_cache", {})
        if obj.id not in cache:
            cache[obj.id] = obj.subjects.filter(lessons__statut=StatutContenu.VALIDE).exists()
        return cache[obj.id]


class FiliereSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filiere
        fields = ["id", "code", "label"]


class SeriesSerializer(serializers.ModelSerializer):
    filiere = FiliereSerializer(read_only=True)

    class Meta:
        model = Series
        fields = ["id", "code", "label", "groupe", "filiere"]


class SubjectSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)

    class Meta:
        model = Subject
        fields = ["id", "code", "label", "country"]


class SubjectListSerializer(SubjectSerializer):
    """
    SubjectSerializer + le volume de cours publiés, pour /catalog/subjects/ seulement.

    Sérialiseur distinct plutôt qu'un champ ajouté à SubjectSerializer : ce dernier est
    imbriqué dans CoursSerializer et LessonSerializer, où chaque objet de la page
    porterait alors un compteur inutile - et déclencherait une requête par ligne, faute
    de l'annotation que seule la vue liste des matières pose.
    """

    # Jamais un SerializerMethodField qui compterait lui-même : la valeur vient de
    # l'annotation de SubjectListView, et une matière servie sans cette annotation doit
    # échouer bruyamment plutôt que d'inventer un 0 silencieux.
    cours_count = serializers.IntegerField(read_only=True)

    class Meta(SubjectSerializer.Meta):
        fields = [*SubjectSerializer.Meta.fields, "cours_count"]


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
        # Mémoïsé par (pays, examen) sur le contexte de sérialisation (même patron que
        # CountrySerializer.get_has_lessons ci-dessus) - obj.display_examen() (voir
        # resolve_examen_label dans catalog.models) interroge ExamenLabel à chaque
        # appel, et une page d'épreuves référence souvent le même (pays, examen) pour
        # plusieurs Cursus distincts (une série différente par Cursus, même examen).
        cache = self.context.setdefault("_examen_display_cache", {})
        key = (obj.country_id, obj.examen)
        if key not in cache:
            cache[key] = obj.display_examen()
        return cache[key]


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
        if self._est_vitrine(obj):
            return True
        user = self._current_user()
        if user is None:
            return False
        # active_subscription_cursus_ids : ensemble des cursus couverts par un
        # abonnement actif, calculé une fois par requête HTTP (voir
        # access.services.bulk_active_subscription_cursus_ids) plutôt qu'un aller en
        # base par objet - même correctif que _est_vitrine ci-dessus, pour tout
        # utilisateur connecté cette fois (pas seulement l'anonyme). obj.cursus est
        # déjà prefetch_related sur les vues liste, donc `.all()` ici ne coûte rien.
        active_cursus_ids = self.context.get("active_subscription_cursus_ids")
        if active_cursus_ids is not None:
            obj_cursus_ids = [c.pk for c in obj.cursus.all()]
            if not obj_cursus_ids:
                return bool(active_cursus_ids)
            return any(cid in active_cursus_ids for cid in obj_cursus_ids)
        return bool(has_access(user, obj))

    def _est_vitrine(self, obj):
        # est_vitrine est un champ réel (donc gratuit) sur Lesson, mais une @property
        # recalculée par une vraie requête à chaque accès sur Cours (voir
        # Cours.est_vitrine, "jamais stocké"). Sur une page de related_cours, les Cours
        # référencés sont presque tous DISTINCTS d'une Lesson à l'autre (peu de
        # doublons à dédupliquer) : un simple cache par objet ne suffit pas, il faut
        # une vraie requête groupée - voir bulk_cours_est_vitrine, posée dans le
        # contexte par LessonListView.list pour toute la page en un seul aller. Repli
        # sur la property (LessonDetailView, CoursDetailView, CoursListView - un seul
        # ou peu d'objets, coût négligeable) quand ce bulk n'est pas fourni.
        bulk_ids = self.context.get("est_vitrine_ids")
        if bulk_ids is not None and isinstance(obj, Cours):
            return obj.pk in bulk_ids
        return bool(getattr(obj, "est_vitrine", False))

    def get_is_read(self, obj):
        user = self._current_user()
        if user is None:
            return False
        # read_lesson_ids/read_cours_ids : mêmes correctif et raison que
        # active_subscription_cursus_ids ci-dessus (voir access.services.bulk_read_ids),
        # posés dans le contexte par les vues liste pour toute la page en un seul aller.
        key = "read_cours_ids" if isinstance(obj, Cours) else "read_lesson_ids"
        read_ids = self.context.get(key)
        if read_ids is not None:
            return obj.pk in read_ids
        return bool(obj.lectures.filter(user=user).exists())


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
    partie_epreuve_francais_display = serializers.CharField(source="get_partie_epreuve_francais_display", read_only=True)
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
            "etablissement", "institution", "nature_epreuve", "nature_epreuve_display",
            "partie_epreuve_francais", "partie_epreuve_francais_display", "themes",
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
        # bulk_lesson_exercises_counts pré-calculé par LessonListView.list pour toute
        # la page en une seule requête (voir ce nom plus bas) - jamais posé par
        # LessonDetailView (un seul objet, une requête directe reste la plus simple).
        counts_map = self.context.get("exercises_count_map")
        if counts_map is not None:
            return counts_map.get(obj.id, 0)
        return obj.exercises.filter(statut=StatutContenu.VALIDE).count()

    def get_sujet_pdf_url(self, obj):
        # Généré hors ligne (voir catalog/sujet_pdf.py) : null tant que la commande/
        # action admin ne l'a pas encore produit, jamais généré à la demande ici.
        if not obj.sujet_pdf:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.sujet_pdf.url) if request else obj.sujet_pdf.url

    def get_related_cours(self, obj):
        # bulk_related_cours_map pré-calculé par LessonListView.list pour toute la
        # page en une seule requête (voir ce nom plus bas) - jamais posé par
        # LessonDetailView, qui garde la requête directe ci-dessous (un seul objet).
        cours_map = self.context.get("related_cours_map")
        if cours_map is not None:
            cours_list = cours_map.get(obj.id, [])
        else:
            cours_list = Cours.objects.filter(
                rappels_source__exercise__lesson=obj, statut=StatutContenu.VALIDE,
            ).distinct()
        return CoursSummarySerializer(cours_list, many=True, context=self.context).data


def bulk_lesson_exercises_counts(lesson_ids):
    """Une seule requête agrégée pour tout un lot, plutôt qu'un .exercises.count() par
    Lesson (voir LessonSerializer.get_exercises_count et LessonListView.list - même
    correctif que inedit_bridge.bulk_exercises_counts côté EpreuveInedite)."""
    counts = (
        Exercise.objects.filter(lesson_id__in=lesson_ids, statut=StatutContenu.VALIDE)
        .values("lesson_id")
        .annotate(n=Count("id"))
    )
    return {row["lesson_id"]: row["n"] for row in counts}


def bulk_cours_est_vitrine(cours_ids):
    """Une seule requête pour tout un lot de Cours, plutôt qu'une évaluation de la
    @property Cours.est_vitrine (jamais stockée, voir ce nom dans catalog.models) par
    objet - voir _HasAccessMixin._est_vitrine, où ce coût se répète une fois par Cours
    DISTINCT référencé dans related_cours (majoritairement des objets distincts d'une
    Lesson à l'autre sur ce corpus, donc un simple cache par objet n'aurait presque
    rien économisé)."""
    if not cours_ids:
        return set()
    return set(
        RappelDeMethode.objects.filter(
            cours_id__in=cours_ids, exercise__lesson__est_vitrine=True,
        ).values_list("cours_id", flat=True).distinct()
    )


def bulk_related_cours_map(lesson_ids):
    """Une seule requête (+ un fetch groupé des Cours distincts) pour tout un lot,
    plutôt qu'un Cours.objects.filter(...) par Lesson (voir
    LessonSerializer.get_related_cours et LessonListView.list)."""
    pairs = list(
        RappelDeMethode.objects.filter(
            exercise__lesson_id__in=lesson_ids, cours__statut=StatutContenu.VALIDE,
        ).values_list("exercise__lesson_id", "cours_id").distinct()
    )
    cours_ids = {cours_id for _, cours_id in pairs}
    # prefetch_related("cursus") : évite qu'une Cours partagée par plusieurs Lesson de
    # la page ne redéclenche has_access (obj.cursus.all()) une fois par Lesson.
    cours_by_id = {c.id: c for c in Cours.objects.filter(id__in=cours_ids).prefetch_related("cursus")}
    result = {}
    for lesson_id, cours_id in pairs:
        result.setdefault(lesson_id, []).append(cours_by_id[cours_id])
    return result


class CoursSerializer(_HasAccessMixin, serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    cursus = CursusSerializer(read_only=True, many=True)
    tags = TagSerializer(many=True, read_only=True)
    has_access = serializers.SerializerMethodField()
    is_read = serializers.SerializerMethodField()
    apercu_contenu = serializers.SerializerMethodField()
    # SerializerMethodField plutôt que le ReadOnlyField auto-généré par ModelSerializer
    # pour une @property (voir Cours.est_vitrine, "jamais stockée") : ce dernier
    # appellerait obj.est_vitrine directement, une vraie requête à chaque ligne, sans
    # jamais passer par _HasAccessMixin._est_vitrine ni son cache/bulk ci-dessus -
    # c'était encore le cas jusqu'ici même après le correctif sur get_has_access.
    est_vitrine = serializers.SerializerMethodField()

    class Meta:
        model = Cours
        fields = [
            "id", "slug", "titre", "subject", "cursus", "sous_theme",
            "duree_estimee_min", "tags", "has_access", "is_read", "est_vitrine", "apercu_contenu", "created_at",
        ]

    def get_apercu_contenu(self, obj):
        return _cours_content_summary(obj.sections_raw)

    def get_est_vitrine(self, obj):
        return self._est_vitrine(obj)
