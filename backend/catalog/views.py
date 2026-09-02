from django.db.models import Count, Exists, IntegerField, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from access.services import has_access, has_access_jusqua_examen
from quiz.models import CompetenceItem

from .inedit_bridge import (
    bulk_exercises_counts,
    bulk_related_cours_map as bulk_related_cours_map_inedit,
    build_inedit_queryset,
    epreuve_inedite_catalogue_payload,
)
from .models import (
    Cours,
    Country,
    Cursus,
    Lesson,
    LessonType,
    Origine,
    Question,
    StatutContenu,
    Subject,
    SUBJECT_FAMILIES,
    Tag,
    Temoignage,
)
from .serializers import (
    bulk_cours_est_vitrine,
    bulk_lesson_exercises_counts,
    bulk_related_cours_map,
    CoursSerializer,
    CountrySerializer,
    CursusSerializer,
    LessonSerializer,
    SubjectListSerializer,
    TemoignageSerializer,
)


# ?ordering=popular (voir LessonListView ci-dessous) : nombre minimum de lecteurs
# distincts (access.LectureProgress) avant qu'une Lesson entre dans le classement
# "populaire" - sans ce seuil, 1-2 lectures de test suffiraient à qualifier un
# contenu comme "populaire", un signal statistiquement creux et trompeur pour un
# visiteur. Tant qu'aucune Lesson ne l'atteint, ?ordering=popular renvoie une liste
# vide plutôt qu'un classement arbitraire - le rail correspondant côté frontend
# disparaît alors silencieusement (même patron que "Corrigés gratuits"). Réutilisé
# tel quel côté EpreuveInedite (voir build_inedit_queryset) - un seuil unique, jamais
# deux constantes qui pourraient diverger.
MIN_POPULAR_READERS = 3


def _merge_sort_key(ordering):
    """Clé de tri pour la liste fusionnée Lesson + EpreuveInedite (voir
    LessonListView.list) - remplace les .order_by() de get_queryset(), impossibles une
    fois les deux querysets combinés en liste Python. Opère sur les valeurs BRUTES
    (year/title/created_at/popularity) capturées avant sérialisation, jamais sur le
    dict déjà sérialisé : created_at y devient une chaîne ISO (DRF DateTimeField), pas
    un datetime - comparer les objets source évite cette ambiguïté de format. Une
    EpreuveInedite (year=None) est toujours reléguée en fin de tri "year"/défaut -
    décision produit actée : le tri par défaut reste par année d'examen, les inédites
    restent découvrables via le filtre origine=INEDITE et le rail "Derniers ajouts"."""
    if ordering == "year":
        return lambda e: ((1, 0) if e["year"] is None else (0, e["year"]), e["title"])
    if ordering == "recent":
        return lambda e: -e["created_at"].timestamp()
    if ordering == "popular":
        def key(e):
            year_key = (1, 0) if e["year"] is None else (0, -e["year"])
            return (-(e["popularity"] or 0), year_key)
        return key
    # défaut = Lesson.Meta.ordering (["-year", "title"]) - décision produit : inchangé.
    return lambda e: ((1, 0) if e["year"] is None else (0, -e["year"]), e["title"])


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
        if discipline := params.get("discipline"):
            # "Contient cette discipline" plutôt qu'une correspondance exacte : Physique
            # inclut aussi les épreuves classées Physique-Chimie (voir SUBJECT_FAMILIES),
            # contrairement à ?subject= qui reste une correspondance stricte - ?subject=
            # PHYSIQUE exclut volontairement Physique-Chimie. Une discipline hors famille
            # (ex. Maths) se comporte comme ?subject= (famille réduite à elle-même).
            discipline_code = discipline.upper()
            family = {discipline_code, SUBJECT_FAMILIES.get(discipline_code, discipline_code)}
            qs = qs.filter(subject__code__in=family)
        if cursus_id := params.get("cursus"):
            qs = qs.filter(cursus__id=cursus_id)
        if country := params.get("country"):
            qs = qs.filter(cursus__country__code__iexact=country)
        if lesson_type := params.get("lesson_type"):
            qs = qs.filter(lesson_type=lesson_type)
        if origine := params.get("origine"):
            qs = qs.filter(origine=origine)
        if nature := params.get("nature"):
            qs = qs.filter(nature_epreuve=nature.upper())
        if partie_francais := params.get("partie_francais"):
            qs = qs.filter(partie_epreuve_francais=partie_francais.upper())
        if params.get("est_vitrine") == "true":
            # Sert le CTA "Essayer un corrigé gratuit" du hero (CataloguePage) : trouver
            # un corrigé en accès libre pour ce pays sans avoir à connaître son slug à
            # l'avance côté frontend.
            qs = qs.filter(est_vitrine=True)
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
        elif params.get("ordering") == "recent":
            # Distinct de -year (Meta.ordering par défaut) : l'année de l'épreuve n'a
            # aucun rapport avec la date à laquelle son corrigé a été ajouté à la
            # plateforme (voir l'audit UX, rail "Derniers ajouts") - un vieux sujet tout
            # juste corrigé doit pouvoir apparaître comme un ajout récent.
            qs = qs.order_by("-created_at")
        elif params.get("ordering") == "popular":
            # Nombre de lecteurs distincts, jamais exposé tel quel au frontend (voir
            # LessonSerializer.Meta.fields, qui ne l'inclut pas) - sert uniquement à
            # trier/filtrer ici, jamais affiché comme "N élèves l'ont lu" (même
            # principe que PlatformStatsView : pas de métrique d'engagement par
            # utilisateur rendue publique). Anonyme non compté : LectureProgress
            # n'existe que pour un utilisateur authentifié (voir access.views.read_lesson).
            qs = (
                qs.annotate(_lectures_count=Count("lectures", distinct=True))
                .filter(_lectures_count__gte=MIN_POPULAR_READERS)
                .order_by("-_lectures_count", "-year")
            )
        if search := params.get("search"):
            # Plein texte : titre, contenu compilé, thèmes et mots-clés - pas seulement
            # le titre, pour qu'une recherche par notion ("discriminant") trouve les
            # corrigés qui la traitent même si elle n'apparaît pas dans le titre.
            #
            # EXISTS() (sous-requête corrélée), jamais un JOIN, pour themes/mots_cles_
            # recherche : joindre CES DEUX relations M2M en même temps dans un seul
            # filtre multiplie chaque Lesson par (nb thèmes × nb mots-clés) avant même
            # d'évaluer le WHERE - jusqu'à ~2800 lignes fantômes pour une seule épreuve
            # sur ce corpus, avec le test sur content_markdown (gros TEXT) alors réévalué
            # une fois par ligne fantôme au lieu d'une fois par épreuve. Mesuré en
            # conditions réelles : recherche "2022" sur ~225 épreuves passée de 107s
            # (JOIN+DISTINCT, 217 082 lignes intermédiaires) à quelques millisecondes.
            theme_match = Tag.objects.filter(lessons_as_theme=OuterRef("pk"), name__icontains=search)
            keyword_match = Tag.objects.filter(lessons_as_keyword=OuterRef("pk"), name__icontains=search)
            qs = qs.filter(
                Q(title__icontains=search)
                | Q(content_markdown__icontains=search)
                | Exists(theme_match)
                | Exists(keyword_match),
            )
        if theme := params.get("theme"):
            # Lien "s'entraîner sur ce thème" depuis le classement des thèmes fréquents
            # (voir ThemesFrequentsView) - correspondance exacte sur Question.themes
            # (pas Lesson.themes/mots_cles_recherche, moins précis) : même patron EXISTS()
            # corrélé que ?search= ci-dessus, pour la même raison (éviter le JOIN M2M qui
            # multiplie chaque Lesson par son nombre de Question taguées).
            theme_question_match = Question.objects.filter(exercise__lesson=OuterRef("pk"), themes__name=theme)
            qs = qs.filter(Exists(theme_question_match))

        return qs.distinct()

    def list(self, request, *args, **kwargs):
        """Fusionne Lesson (classique) et EpreuveInedite dans une seule liste
        paginée/triée - voir l'audit "Fusion du catalogue". get_queryset() ci-dessus
        reste inchangé (toujours filtré/annoté côté SQL) ; le côté EpreuveInedite est
        construit en miroir par build_inedit_queryset.

        Le tri à cheval sur deux tables reste impossible à exprimer en un seul
        ORDER BY (voir _merge_sort_key) - mais SEULES des clés de tri légères
        (id/year/title/created_at/popularité, via .values()) sont matérialisées pour
        calculer cet ordre sur l'ENSEMBLE filtré : ni select_related/prefetch_related,
        ni sérialisation (get_exercises_count, get_related_cours, CountrySerializer
        imbriqué...) n'y sont payés. La pagination tranche ensuite ces clés, et seule la
        page obtenue (24 items par défaut) déclenche le fetch complet + la
        sérialisation coûteuse - jamais l'ensemble filtré. Avant ce correctif, un
        catalogue sans filtre (543 items) coûtait jusqu'à 9000 requêtes SQL et ~40s
        pour une seule page, la pagination étant appliquée en tout dernier sur la liste
        déjà entièrement sérialisée (voir l'audit perf "catalogue lent")."""
        ordering = request.query_params.get("ordering")
        context = self.get_serializer_context()

        lesson_qs = self.get_queryset()
        inedit_qs = build_inedit_queryset(request.query_params, min_popular_readers=MIN_POPULAR_READERS)

        lesson_value_fields = ["id", "year", "title", "created_at"]
        if ordering == "popular":
            lesson_value_fields.append("_lectures_count")
        lesson_keys = [
            {
                "kind": "lesson", "id": row["id"], "year": row["year"], "title": row["title"],
                "created_at": row["created_at"], "popularity": row.get("_lectures_count") or 0,
            }
            for row in lesson_qs.values(*lesson_value_fields)
        ]

        inedit_value_fields = ["id", "titre", "created_at"]
        if ordering == "popular":
            inedit_value_fields.append("_tentatives_count")
        inedit_keys = [
            {
                "kind": "inedite", "id": row["id"], "year": None, "title": row["titre"],
                "created_at": row["created_at"], "popularity": row.get("_tentatives_count") or 0,
            }
            for row in inedit_qs.values(*inedit_value_fields)
        ]

        merged_keys = lesson_keys + inedit_keys
        merged_keys.sort(key=_merge_sort_key(ordering))

        page_keys = self.paginate_queryset(merged_keys)
        keys_to_serialize = page_keys if page_keys is not None else merged_keys

        page_lesson_ids = [k["id"] for k in keys_to_serialize if k["kind"] == "lesson"]
        page_inedit_ids = [k["id"] for k in keys_to_serialize if k["kind"] == "inedite"]

        lesson_payloads_by_id = {}
        if page_lesson_ids:
            lesson_objs_by_id = {obj.id: obj for obj in lesson_qs.filter(id__in=page_lesson_ids)}
            ordered_lesson_objs = [lesson_objs_by_id[i] for i in page_lesson_ids if i in lesson_objs_by_id]
            related_cours_map = bulk_related_cours_map(page_lesson_ids)
            related_cours_ids = {c.pk for cours_list in related_cours_map.values() for c in cours_list}
            page_context = {
                **context,
                "exercises_count_map": bulk_lesson_exercises_counts(page_lesson_ids),
                "related_cours_map": related_cours_map,
                "est_vitrine_ids": bulk_cours_est_vitrine(related_cours_ids),
            }
            payloads = LessonSerializer(ordered_lesson_objs, many=True, context=page_context).data
            lesson_payloads_by_id = {obj.id: payload for obj, payload in zip(ordered_lesson_objs, payloads)}

        inedit_payloads_by_id = {}
        if page_inedit_ids:
            inedit_objs = list(inedit_qs.filter(id__in=page_inedit_ids))
            exercises_counts = bulk_exercises_counts(inedit_objs)
            inedit_related_cours_map = bulk_related_cours_map_inedit(page_inedit_ids)
            inedit_related_cours_ids = {c.pk for cours_list in inedit_related_cours_map.values() for c in cours_list}
            inedit_context = {**context, "est_vitrine_ids": bulk_cours_est_vitrine(inedit_related_cours_ids)}
            inedit_payloads_by_id = {
                obj.id: epreuve_inedite_catalogue_payload(
                    obj, request, exercises_count=exercises_counts.get(obj.id, 0),
                    related_cours=inedit_related_cours_map.get(obj.id, []),
                    context=inedit_context,
                )
                for obj in inedit_objs
            }

        payload_list = [
            lesson_payloads_by_id[k["id"]] if k["kind"] == "lesson" else inedit_payloads_by_id[k["id"]]
            for k in keys_to_serialize
            if (k["id"] in lesson_payloads_by_id if k["kind"] == "lesson" else k["id"] in inedit_payloads_by_id)
        ]

        if page_keys is not None:
            return self.get_paginated_response(payload_list)
        return Response(payload_list)


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
        if params.get("exclude_read") == "true" and self.request.user.is_authenticated:
            # Même repli anonyme naturel que LessonListView ci-dessus - pas de
            # LectureProgress à exclure pour un visiteur non connecté.
            qs = qs.exclude(lectures__user=self.request.user)
        if search := params.get("search"):
            # EXISTS() plutôt qu'un JOIN sur tags - même raison que LessonListView
            # ci-dessus (évite de réévaluer content_markdown une fois par tag au lieu
            # d'une fois par Cours).
            tag_match = Tag.objects.filter(cours=OuterRef("pk"), name__icontains=search)
            qs = qs.filter(
                Q(titre__icontains=search)
                | Q(content_markdown__icontains=search)
                | Exists(tag_match),
            )

        # Plus récent d'abord - remplace l'ordre alphabétique par défaut de Cours.Meta
        # (utile pour l'admin, pas pour un visiteur qui veut voir les derniers cours
        # ajoutés). published_at n'est jamais renseigné en pratique (aucun code ne
        # l'écrit) donc pas fiable pour ce tri, contrairement à created_at.
        return qs.distinct().order_by("-created_at")


class CoursDetailView(generics.RetrieveAPIView):
    serializer_class = CoursSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Cours.objects.visibles().select_related(
        "subject__country",
    ).prefetch_related("cursus__series", "cursus__country", "tags")

    def get_object(self):
        qs = self.filter_queryset(self.get_queryset()).par_slug_ou_id(self.kwargs["slug"])
        obj = get_object_or_404(qs)
        self.check_object_permissions(self.request, obj)
        return obj


class SubjectListView(generics.ListAPIView):
    serializer_class = SubjectListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        cours_publies = Cours.objects.filter(subject=OuterRef("pk"), statut=StatutContenu.VALIDE)
        lessons_publiees = Lesson.objects.filter(subject=OuterRef("pk"), statut=StatutContenu.VALIDE)

        # Ne propose que les matières ayant déjà du contenu publié (Épreuve ou Cours) -
        # même principe que CountrySerializer.get_has_lessons, sinon le select liste
        # surtout des matières vides (référentiel Subject bien plus large que le
        # contenu réellement ingéré à date).
        #
        # Exists() plutôt que .filter(Q(lessons) | Q(cours)).distinct() : ce dernier
        # joignait réellement les deux tables, produisant une ligne par couple
        # (épreuve, cours) de la matière avant dédoublonnage - des millions de lignes
        # pour les Mathématiques. Tant que le SELECT restait trivial, PostgreSQL
        # encaissait ; en y ajoutant `cours_count` (sous-requête corrélée, donc
        # évaluée AVANT le DISTINCT, une fois par ligne de la jointure), l'endpoint est
        # passé de quelques centaines de millisecondes à un WORKER TIMEOUT gunicorn -
        # bug réel, constaté en local le 2026-08-17. Sans jointure il n'y a plus de
        # doublons à écarter, donc plus de DISTINCT, et la sous-requête ne tourne
        # qu'une fois par matière.
        qs = (
            Subject.objects.select_related("country")
            .filter(country__actif=True)
            .filter(Exists(lessons_publiees) | Exists(cours_publies))
            # Coalesce : une matière qui n'a que des épreuves et aucun cours ne remonte
            # aucune ligne de la sous-requête, donc NULL - jamais servi tel quel, le
            # client attend un entier (un tri sur null casserait l'ordre des pastilles
            # de matière côté /cours).
            .annotate(
                cours_count=Coalesce(
                    Subquery(
                        cours_publies.values("subject").annotate(n=Count("pk")).values("n"),
                        output_field=IntegerField(),
                    ),
                    0,
                ),
            )
        )
        if country := self.request.query_params.get("country"):
            qs = qs.filter(country__code__iexact=country)
        return qs


class CountryListView(generics.ListAPIView):
    queryset = Country.objects.filter(actif=True)
    serializer_class = CountrySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class TemoignageListView(generics.ListAPIView):
    queryset = Temoignage.objects.publies()
    serializer_class = TemoignageSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class PlatformStatsView(APIView):
    """
    Chiffres publics agrégés (page d'accueil / tarifs, preuve sociale - voir l'audit
    UX, reco 8.3). Uniquement des comptages de contenu réel, jamais un nombre
    d'abonnés ou d'élèves : une métrique business sensible que l'équipe n'a pas
    choisi d'exposer publiquement.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        contenu_valide = Q(statut=StatutContenu.VALIDE, subject__country__actif=True)
        return Response({
            "corriges_disponibles": Lesson.objects.filter(contenu_valide, lesson_type=LessonType.CORR).count(),
            "cours_disponibles": Cours.objects.filter(contenu_valide).count(),
            "pays_actifs": Country.objects.filter(actif=True).count(),
        })


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


# En dessous, le signal n'est pas fiable - mesuré en pratique sur SVT BAC D Cameroun
# (seulement 5 épreuves officielles en base, occurrence maximale de 2) : "tombé 2 fois
# sur 5" sonnerait comme une fausse promesse plutôt que comme une vraie récurrence.
SEUIL_MINIMUM_THEMES_FREQUENTS = 8
TEASER_THEMES_FREQUENTS = 2
MAX_THEMES_FREQUENTS = 20


class ThemesFrequentsView(APIView):
    """
    Classement des thèmes (Tag) les plus fréquents aux épreuves officielles d'un
    (cursus, matière) donné - argument de vente propre au palier Jusqu'à l'Examen (voir
    access.services.has_access_jusqua_examen). Toujours AllowAny : un visiteur ou un
    abonné Mensuel voit un teaser de TEASER_THEMES_FREQUENTS thèmes, la liste complète
    n'est renvoyée qu'à un abonné Jusqu'à l'Examen actif sur ce cursus précis - jamais
    deux payloads différents pour la même requête selon un champ caché, le classement
    complet est toujours calculé côté serveur puis tronqué ou non (même principe que
    access.views.read_lesson/preview_lesson : un seul point de calcul, une troncature
    déterministe selon l'accès, jamais un second calcul "allégé" qui pourrait diverger).

    Agrégation par ÉPREUVE (Lesson), jamais par Question : un thème traité 3 fois dans
    le même sujet ne doit compter qu'une fois, sinon un exercice bavard fausse la
    fréquence. Restreint à origine=OFFICIEL - un examen blanc ou une épreuve
    d'établissement ne dit rien de ce qui tombe réellement à l'examen. Les deux règles
    ont été validées à la main sur le corpus réel (Maths BAC C, Anglais BAC C-D) avant
    d'écrire cet endpoint.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, cursus_id):
        cursus = get_object_or_404(Cursus.objects.select_related("country"), pk=cursus_id)
        if not cursus.country.actif:
            return Response({"error": "Ce cursus n'est pas disponible."}, status=404)

        # Code (ex. "MATHS"), pas le pk : même identifiant que ?subject= sur
        # /catalog/lessons/ (voir LessonListView) - le frontend le tient déjà de
        # listSubjects(), pas besoin d'une résolution séparée. Scopé au pays du
        # cursus : Subject.code n'est unique que par (country, code).
        subject_code = request.query_params.get("subject")
        if not subject_code:
            return Response({"error": "subject est requis."}, status=400)
        subject = get_object_or_404(Subject, code=subject_code, country=cursus.country)

        lessons = Lesson.objects.filter(
            statut=StatutContenu.VALIDE, origine=Origine.OFFICIEL, subject=subject, cursus=cursus,
        ).distinct()
        nb_sessions_disponibles = lessons.count()

        if nb_sessions_disponibles < SEUIL_MINIMUM_THEMES_FREQUENTS:
            return Response({
                "nb_sessions_disponibles": nb_sessions_disponibles,
                "seuil_minimum": SEUIL_MINIMUM_THEMES_FREQUENTS,
                "disponible": False,
                "has_access": False,
                "nb_themes_verrouilles": 0,
                "themes": [],
            })

        classement = list(
            Tag.objects.filter(questions_as_theme__exercise__lesson__in=lessons)
            .annotate(nb_epreuves=Count("questions_as_theme__exercise__lesson", distinct=True))
            .order_by("-nb_epreuves", "name")[:MAX_THEMES_FREQUENTS],
        )

        acces_jusqua_examen = has_access_jusqua_examen(request.user, cursus)
        themes_visibles = classement if acces_jusqua_examen else classement[:TEASER_THEMES_FREQUENTS]

        # Un thème du classement peut n'avoir aucune CompetenceItem sur SON tag - deux
        # vocabulaires de tags coexistent dans le catalogue (voir quiz.views, même
        # cascade pour résoudre le cours lié à une compétence) : correction-experte pose
        # des tags de TECHNIQUE sur les questions ("tableau de variation"), le Quiz porte
        # des tags de CHAPITRE alignés sur les savoirs ("dérivation"). Un thème sans
        # correspondance directe peut donc avoir une vraie compétence dispo sous un tag
        # différent, via le même savoir_officiel. Mesuré avant ce correctif : sur le top
        # 20 de Maths BAC C, 10/20 thèmes étaient à tort marqués indisponibles alors
        # qu'une compétence existait déjà - ne jamais retester seulement le tag exact.
        tags_avec_quiz_direct = set(
            CompetenceItem.objects.filter(
                theme_id__in=[t.id for t in themes_visibles], cursus=cursus, statut=StatutContenu.VALIDE,
            ).values_list("theme_id", flat=True),
        )
        savoirs_a_verifier = {
            t.savoir_officiel_id for t in themes_visibles
            if t.id not in tags_avec_quiz_direct and t.savoir_officiel_id is not None
        }
        savoirs_avec_quiz = set()
        if savoirs_a_verifier:
            savoirs_avec_quiz = set(
                CompetenceItem.objects.filter(
                    theme__savoir_officiel_id__in=savoirs_a_verifier, cursus=cursus, statut=StatutContenu.VALIDE,
                ).values_list("theme__savoir_officiel_id", flat=True),
            )
        tags_avec_quiz = tags_avec_quiz_direct | {
            t.id for t in themes_visibles if t.savoir_officiel_id in savoirs_avec_quiz
        }

        return Response({
            "nb_sessions_disponibles": nb_sessions_disponibles,
            "seuil_minimum": SEUIL_MINIMUM_THEMES_FREQUENTS,
            "disponible": True,
            "has_access": acces_jusqua_examen,
            "nb_themes_verrouilles": 0 if acces_jusqua_examen else max(0, len(classement) - TEASER_THEMES_FREQUENTS),
            "themes": [
                {
                    "id": t.id,
                    "tag": t.name,
                    "nb_epreuves": t.nb_epreuves,
                    "frequence_pct": round(100 * t.nb_epreuves / nb_sessions_disponibles),
                    "quiz_disponible": t.id in tags_avec_quiz,
                }
                for t in themes_visibles
            ],
        })


class ThemeExercicesView(APIView):
    """
    Exercices concernés par un thème donné, pour un (cursus, matière) - alimente le
    bouton "Exercices" à côté de chaque thème de ThemesFrequentsView (qui expose l'id
    du Tag nécessaire ici). Contrairement au classement, aucune restriction
    origine=OFFICIEL ni seuil minimum : l'objectif est de fournir un support
    d'entraînement concret, pas une statistique de fréquence à l'examen réel - un
    examen blanc qui traite le thème est tout aussi utile à pratiquer. Toujours
    AllowAny : chaque exercice porte son propre has_access (comme EpreuveCard), le
    frontend décide alors du lien (lecteur si accès, fiche détail sinon).
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, cursus_id, tag_id):
        cursus = get_object_or_404(Cursus.objects.select_related("country"), pk=cursus_id)
        if not cursus.country.actif:
            return Response({"error": "Ce cursus n'est pas disponible."}, status=404)

        subject_code = request.query_params.get("subject")
        if not subject_code:
            return Response({"error": "subject est requis."}, status=400)
        subject = get_object_or_404(Subject, code=subject_code, country=cursus.country)
        tag = get_object_or_404(Tag, pk=tag_id)

        questions = (
            Question.objects.filter(
                themes=tag, exercise__lesson__statut=StatutContenu.VALIDE,
                exercise__lesson__subject=subject, exercise__lesson__cursus=cursus,
            )
            .select_related("exercise__lesson")
            .order_by("-exercise__lesson__year", "exercise__numero_exercice")
        )

        # Un exercice bavard peut porter le thème sur plusieurs de ses Question - une
        # seule entrée par exercice, jamais par question (même principe que
        # ThemesFrequentsView : l'unité pertinente pour l'élève est "un exercice à
        # pratiquer", pas chacune de ses sous-questions).
        vus = set()
        exercices = []
        for question in questions:
            lesson = question.exercise.lesson
            cle = (lesson.id, question.exercise.numero_exercice)
            if cle in vus:
                continue
            vus.add(cle)
            exercices.append({
                "lesson_slug": lesson.slug,
                "lesson_title": lesson.title,
                "lesson_year": lesson.year,
                "numero_exercice": question.exercise.numero_exercice,
                "has_access": has_access(request.user, lesson),
            })

        return Response({"tag": tag.name, "exercices": exercices})
