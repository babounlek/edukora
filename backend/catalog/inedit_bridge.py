"""
Pont catalog <-> inedit pour le catalogue unifié (/catalog/lessons/, voir
catalog.views.LessonListView.list) - seul fichier de catalog qui importe depuis inedit,
pour ne pas disperser cette dépendance dans get_queryset() (logique Lesson déjà dense et
testée, laissée intacte). Réutilisé tel quel par inedit.views.epreuve_inedite_detail -
même mapping de champs pour la fiche détail que pour la liste, jamais dupliqué.
"""

from django.db.models import Count

from access.services import has_access_inedite
from inedit.models import EpreuveInedite, ExerciceInedite

from .models import Cours, StatutContenu, SUBJECT_FAMILIES
from .serializers import CoursSummarySerializer, CursusSerializer, SubjectSerializer, TagSerializer


def build_inedit_queryset(params, *, min_popular_readers):
    """Miroir de LessonListView.get_queryset() côté EpreuveInedite. Un paramètre
    structurellement incompatible avec ce modèle (lesson_type/origine classique/nature/
    est_vitrine) fait dégénérer le résultat en queryset vide (.none()) - jamais une
    erreur 400 : /catalog/lessons/?lesson_type=FICHE doit rester un 200 avec une liste
    partiellement vide côté inédit, pas un crash."""
    qs = (
        EpreuveInedite.objects.filter(statut=StatutContenu.VALIDE, cursus__country__actif=True)
        .select_related("subject__country", "blueprint")
        .prefetch_related("cursus__series", "cursus__country", "blueprint__competences")
    )

    if params.get("lesson_type") or params.get("nature") or params.get("est_vitrine") == "true":
        return qs.none()
    origine = params.get("origine")
    if origine and origine != "INEDITE":
        return qs.none()

    if subject := params.get("subject"):
        qs = qs.filter(subject__code=subject)
    if discipline := params.get("discipline"):
        discipline_code = discipline.upper()
        family = {discipline_code, SUBJECT_FAMILIES.get(discipline_code, discipline_code)}
        qs = qs.filter(subject__code__in=family)
    if cursus_id := params.get("cursus"):
        qs = qs.filter(cursus__id=cursus_id)
    if country := params.get("country"):
        qs = qs.filter(cursus__country__code__iexact=country)
    if search := params.get("search"):
        qs = qs.filter(titre__icontains=search)
    # exclude_read : no-op volontaire - EpreuveInedite ne suit aucune "lecture" (voir
    # TentativeInedite, qui suit une tentative, pas une lecture au sens LectureProgress).

    if params.get("ordering") == "popular":
        qs = qs.annotate(_tentatives_count=Count("tentatives", distinct=True)).filter(
            _tentatives_count__gte=min_popular_readers,
        )
    # distinct() : indispensable depuis que EpreuveInedite.cursus est un M2M - les
    # filtres cursus__country__actif/cursus__country__code/cursus__id ci-dessus
    # traversent la table M2M, donc une épreuve commune à plusieurs séries (ex. BAC
    # C/E) produirait une ligne par cursus correspondant sans ce distinct() (même
    # correctif que LessonListView.get_queryset, voir catalog/views.py).
    return qs.distinct()


def bulk_exercises_counts(epreuves):
    """Une seule requête agrégée pour tout un lot, plutôt qu'un .exercices.count() par
    item (évite un N+1 côté liste)."""
    counts = (
        ExerciceInedite.objects.filter(epreuve_id__in=[e.id for e in epreuves])
        .values("epreuve_id")
        .annotate(n=Count("id"))
    )
    return {row["epreuve_id"]: row["n"] for row in counts}


def _apercu_enonce(epreuve):
    """Aperçu public minimal : l'énoncé de la toute première question du premier
    exercice, rien d'autre - jamais l'équivalent de catalog.rendering.
    lesson_preview_markdown (sujet ENTIER, légitime là-bas car ce sont d'anciens
    sujets déjà publics ailleurs). Ici, l'argument de vente d'une Épreuve Inédite est
    justement de n'avoir jamais été vue nulle part (voir EpreuveInediteDetailPage.tsx) :
    en dévoiler l'intégralité gratuitement grillerait à la fois l'exclusivité (contenu
    copiable/partageable avant tout paiement) et l'effet "conditions réelles" pour
    quiconque l'aurait déjà lu. Une seule question suffit à donner le niveau.

    Renvoie aussi le numéro de cet exercice (ExerciceInedite.numero_exercice) - affiché
    en référence sous l'aperçu côté fiche détail, pour que le lecteur sache de quel
    exercice provient l'extrait montré."""
    premier_exercice = epreuve.exercices.order_by("numero_exercice").first()
    if premier_exercice is None:
        return None, None
    premiere_question = premier_exercice.questions.order_by("ordre").first()
    if premiere_question is None:
        return None, None
    return premiere_question.enonce_markdown, premier_exercice.numero_exercice


def epreuve_inedite_catalogue_payload(epreuve, request, *, exercises_count=None, include_apercu=False):
    """Sérialise une EpreuveInedite dans la même forme que LessonSerializer.Meta.fields.
    Réutilisé par le catalogue fusionné (liste) ET inedit.views.epreuve_inedite_detail
    (fiche seule). `exercises_count` pré-calculé pour la liste (voir bulk_exercises_counts) ;
    recalculé à la volée si absent (fiche détail seule - un item, coût négligeable).
    `include_apercu` : coûte 2 requêtes de plus (voir _apercu_enonce) - jamais activé
    pour la liste (un item par carte, inutile à afficher et multiplierait le coût par
    le nombre de cartes), seulement pour la fiche détail (un seul item)."""
    apercu_markdown, apercu_numero_exercice = _apercu_enonce(epreuve) if include_apercu else (None, None)
    payload = {
        "id": epreuve.id,
        "kind": "inedite",
        # Contrairement au commentaire historique du type Epreuve côté frontend
        # ("plusieurs champs classique-only... valent null") : slug est désormais
        # renseigné aussi côté inédit (voir EpreuveInedite.slug) - même URL publique
        # lisible que pour Lesson/Cours, voir epreuveInediteDetailPath.
        "slug": epreuve.slug,
        "title": epreuve.titre,
        "subject": SubjectSerializer(epreuve.subject).data,
        "cursus": CursusSerializer(epreuve.cursus.all(), many=True).data,
        "lesson_type": None,
        "lesson_type_display": "Épreuve inédite",
        "year": None,
        "duree_epreuve": "",
        "coefficient": "",
        "origine": "INEDITE",
        "origine_display": "Épreuve inédite",
        "etablissement": "",
        # Une Épreuve Inédite n'est organisée par aucun office d'examen : elle est
        # conçue et publiée par la plateforme elle-même.
        "institution": "Edukora",
        "nature_epreuve": "",
        "nature_epreuve_display": "",
        "themes": TagSerializer(epreuve.blueprint.competences.all(), many=True).data,
        "has_access": has_access_inedite(request.user, epreuve),
        "is_read": False,
        "est_vitrine": False,
        "created_at": epreuve.created_at,
        "exercises_count": epreuve.exercices.count() if exercises_count is None else exercises_count,
        "related_cours": CoursSummarySerializer(
            Cours.objects.filter(
                rappels_source_inedit__exercice__epreuve=epreuve, statut=StatutContenu.VALIDE,
            ).distinct(),
            many=True, context={"request": request},
        ).data,
        "sujet_pdf_url": None,
        "duree_minutes": epreuve.blueprint.duree_minutes,
        # Voir inedit.views.download_sujet_pdf, seul point de sortie du fichier (jamais
        # une URL de storage renvoyée directement ici, contrairement à sujet_pdf_url
        # côté classique). Proposé sur la fiche épreuve, avant toute tentative - jamais
        # le corrigé, qui reste réservé à InediteResultPage.tsx après coup.
        "sujet_pdf_disponible": bool(epreuve.sujet_pdf),
        # Clé toujours présente (jamais absente du payload liste) pour que le type
        # frontend reste honnête - seule sa VALEUR dépend d'include_apercu, la branche
        # non prise n'appelle jamais _apercu_enonce (voir sa docstring).
        "apercu_enonce_markdown": apercu_markdown,
        "apercu_numero_exercice": apercu_numero_exercice,
    }
    return payload
