from django.db import models
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from catalog import cours_pdf
from catalog.models import Cours, Exercise, Lesson

from quiz import xp
from quiz.models import SourceXP
from users.profils import profil_actif

from . import quota
from .etude import MarqueInvalide, enregistrer_marque, marques_du_document
from .models import ExerciceFait, LectureProgress, MarqueEtude, TelechargementPdf
from .services import a_acces_exercices_cours, has_access
from .sujets_publics import ouvrir_sujet, url_sujet


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
@throttle_classes([quota.LectureThrottle])
def read_lesson(request, lesson_slug):
    """
    Contenu pour lecture en ligne (Markdown) - réservé aux abonnés, sauf une Lesson
    "vitrine" (voir Lesson.est_vitrine), lisible par un visiteur anonyme : AllowAny ici,
    has_access() ci-dessous fait le vrai tri au cas par cas.
    """
    qs = Lesson.objects.visibles().select_related("subject__country").par_slug_ou_id(lesson_slug)
    lesson = get_object_or_404(qs)

    if not has_access(request.user, lesson, profil_actif(request)):
        return Response({"error": "Abonnement requis pour lire ce contenu."}, status=403)

    profil = profil_actif(request) if request.user.is_authenticated else None
    if profil is not None:
        LectureProgress.objects.update_or_create(profil=profil, lesson=lesson)

    # Exercices de CETTE épreuve que le lecteur a déjà déclaré avoir traités - une
    # seule requête pour toute la page. Sert à proposer la validation au bon endroit,
    # à la fin du corrigé (voir access.ExerciceFait) : c'est le seul moment où l'élève
    # a réellement de quoi juger s'il a résolu l'exercice.
    exercices_faits = set()
    if profil is not None:
        exercices_faits = set(
            ExerciceFait.objects.filter(profil=profil, exercise__lesson=lesson)
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
        # Les mêmes consignes de choix sous forme structurée (voir catalog.choix) : l'écran en tire une note
        # lisible au-dessus du sommaire. [] quand toutes les questions sont obligatoires.
        "regles_choix": lesson.regles_choix or [],
        # Énoncé/corrigé par exercice, séparément - voir Lesson.exercises_breakdown.
        # Liste vide pour une Lesson sans Exercise (FICHE...) : le frontend retombe
        # alors sur content_markdown tel quel plutôt que de replier un énoncé qu'on
        # n'a pas isolé.
        "exercises": exercices,
        "header": lesson.header_info(),
        "lesson_type": lesson.lesson_type,
        "sujet_pdf_url": url_sujet(request, lesson),
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
        "regles_choix": lesson.regles_choix or [],
        # Le même sujet, découpé par exercice, pour que la fiche puisse renvoyer
        # directement vers le corrigé de l'exercice lu (/lire#exercice-3) - voir
        # Lesson.preview_exercises, qui n'expose aucun champ de corrigé. Liste vide
        # pour une Lesson sans Exercise : le frontend retombe sur preview_markdown.
        "exercises": lesson.preview_exercises(),
        "header": lesson.header_info(),
    })


@api_view(["GET"])
@permission_classes([AllowAny])
@throttle_classes([quota.LectureThrottle])
def read_cours(request, cours_id):
    """
    Contenu pour lecture en ligne (Markdown) - libre pour tout le monde, visiteur anonyme compris (décision du
    2026-10-14, toute la plateforme) : seule la section « exercices d'application » est payante. Sans abonnement
    sur le cursus du cours (a_acces_exercices_cours), elle est REMPLACÉE côté serveur par un marqueur verrouillé
    (nombre d'exercices et niveaux, jamais leur texte) et le Markdown compilé est reconstruit sans elle : un
    simple masquage à l'écran laisserait les solutions dans la réponse.
    """
    qs = Cours.objects.visibles().select_related("subject__country").par_slug_ou_id(cours_id)
    cours = get_object_or_404(qs)

    if request.user.is_authenticated:
        LectureProgress.objects.update_or_create(profil=profil_actif(request), cours=cours)

    exercices_acces = a_acces_exercices_cours(request.user, cours, profil_actif(request) if request.user.is_authenticated else None)
    return Response({
        "id": cours.id,
        "title": cours.titre,
        "content_markdown": cours.content_markdown if exercices_acces else cours.libre_markdown(),
        # Sections individuellement typées, pour un rendu distinguant visuellement
        # chaque type - voir Cours.sections_breakdown(). Liste vide (cas déjà couvert
        # par le fallback frontend, même convention que EpreuveContent.exercises) si
        # sections_raw est vide : le frontend retombe alors sur content_markdown.
        "sections": cours.sections_breakdown(verrouiller_payantes=not exercices_acces),
        "exercices_acces": exercices_acces,
        "header": cours.header_info(),
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def preview_cours(request, cours_id):
    """Aperçu public : le cours libre (tout sauf les exercices d'application), avec leur marqueur verrouillé."""
    qs = Cours.objects.visibles().select_related("subject__country").par_slug_ou_id(cours_id)
    cours = get_object_or_404(qs)

    return Response({
        "id": cours.id,
        "title": cours.titre,
        "preview_markdown": cours.preview_markdown(),
        "sections": cours.sections_breakdown(verrouiller_payantes=True),
        "header": cours.header_info(),
    })


@api_view(["GET"])
@permission_classes([AllowAny])
@throttle_classes([quota.QuotaThrottle])
def download_cours_pdf(request, cours_id):
    """
    PDF du cours, pour tout le monde (visiteur compris), dans la limite du quota quotidien de PDF (access.quota). La
    VERSION est décidée ici, jamais par le client : avec l'abonnement qui donne les exercices d'application
    (a_acces_exercices_cours) c'est le cours complet, sinon le cours libre, sans eux - la même frontière que read_cours
    (voir catalog.cours_pdf).

    Le PDF est généré à la première demande, hors du thread de la requête : tant qu'il n'existe pas, la réponse est
    202 {"statut": "en_preparation"} et le client réessaie. Quand il existe, il est lu côté serveur et renvoyé
    (jamais l'URL du stockage). Seule la LIVRAISON consomme un crédit : les 202 n'en consomment pas, mais une
    génération n'est lancée que si le demandeur a encore de quoi télécharger (sinon 429 tout de suite).
    """
    if request.method == "HEAD":
        return Response(status=405, headers={"Allow": "GET"})
    qs = Cours.objects.visibles().select_related("subject__country").par_slug_ou_id(cours_id)
    cours = get_object_or_404(qs)

    profil = profil_actif(request) if request.user.is_authenticated else None
    variante = cours_pdf.variante_pour(a_acces_exercices_cours(request.user, cours, profil))
    nom = cours_pdf.nom_fichier(cours, variante)
    stockage = cours_pdf.stockage()
    document = f"cours:{cours.pk}"

    if stockage.exists(nom):
        # Une même adresse sert deux versions selon l'abonnement : jamais mise en cache partagée (livrer_pdf).
        return quota.livrer_pdf(
            request, document, lambda: stockage.open(nom, "rb"),
            as_attachment=True, filename=f"{slugify(cours.titre) or 'cours'}.pdf",
        )

    if not cours_pdf.markdown_du_cours(cours, variante).strip():
        return Response({"error": "Ce cours n'a pas de contenu à imprimer."}, status=404)

    refus = quota.verifier_credit(request, document)
    if refus is not None:
        return refus
    statut = cours_pdf.mettre_en_file(cours, variante)
    if statut == cours_pdf.ECHEC:
        return quota.poser_cookie(request, Response(
            {"error": "Le PDF n'a pas pu être préparé. Réessaie dans quelques minutes."}, status=503,
        ))
    return quota.poser_cookie(request, Response(
        {"statut": statut}, status=202, headers={"Retry-After": "3", "Cache-Control": "no-store"},
    ))


@api_view(["GET"])
@permission_classes([AllowAny])
@throttle_classes([quota.QuotaThrottle])
def download_lesson_sujet_pdf(request, lesson_id):
    """
    PDF du sujet d'une épreuve (jamais le corrigé, voir catalog.sujet_pdf) : public, comme avant, mais servi ICI et
    compté dans le quota quotidien. Le fichier n'est plus joignable par une adresse directe (voir le Caddyfile).
    """
    lesson = get_object_or_404(Lesson.objects.visibles(), pk=lesson_id)
    if not lesson.sujet_pdf:
        return Response({"error": "PDF pas encore généré."}, status=404)
    return quota.livrer_pdf(
        request, f"lesson:{lesson.pk}", lambda: ouvrir_sujet(lesson),
        as_attachment=False, filename=f"{slugify(lesson.title) or 'sujet'}-sujet.pdf",
    )


@api_view(["GET"])
@permission_classes([AllowAny])
@throttle_classes([quota.QuotaThrottle])
def quota_telechargements(request):
    """
    Où en est le demandeur : limite, déjà téléchargés, restants, heure de remise à zéro. Sans effet de bord (ne
    consomme rien) ; pose seulement le cookie du visiteur. ?doc=<type>:<réf> (répétable, 20 au plus) dit en plus quels
    documents sont déjà téléchargés aujourd'hui, donc gratuits à nouveau : cours:<slug|id>, lesson:<id>, inedit:<id>,
    quiz:<id>:sujet|corrige, fiche:<id>:sujet|corrige.
    """
    ctx = quota.contexte(request)
    cles = {}
    for brut in request.query_params.getlist("doc")[:20]:
        type_document, _, reference = brut.partition(":")
        cle = quota.cle_document(type_document, reference)
        if cle:
            cles[brut] = cle
    deja = set(
        TelechargementPdf.objects.filter(jour=ctx.jour, demandeur=ctx.demandeur, document__in=cles.values())
        .values_list("document", flat=True),
    ) if cles else set()
    reponse = Response(quota.etat_json(ctx, gratuits=[brut for brut, cle in cles.items() if cle in deja]))
    return quota.en_tetes(request, reponse)


@api_view(["GET"])
def my_progression(request):
    """
    Leçons et cours dont l'utilisateur a ouvert la lecture complète pour le cursus
    préparé actuellement, du plus récent au plus ancien.

    Filtré sur le cursus préparé actuellement : un compte avec deux abonnements actifs
    (voir le sélecteur d'examen dans Header.tsx/TeteAccueil.tsx) mélangeait sinon les
    lectures des deux cursus dans "Mon historique", "Reprendre ma lecture"
    (CataloguePage, CoursListPage) - une leçon de BEPC lue apparaissait encore une fois
    qu'on avait basculé sur BAC C. Un Cours sans cursus du tout (notion commune à
    toutes les séries, voir Cours.cursus) reste toujours inclus.

    Lu sur `request.user.cursus_prepare` (et non `profil.cursus_prepare`) : c'est le
    champ que le sélecteur d'examen écrit (voir users.serializers.UserProfileUpdateSerializer)
    et que tout le reste de l'app lit encore aujourd'hui (voir quiz.views, "Aujourd'hui")
    - `Profil.cursus_prepare` existe (refonte compte famille en cours) mais n'est pas
    encore la source vivante, les deux ne sont pas synchronisés.
    """
    profil = profil_actif(request)
    cursus = request.user.cursus_prepare if profil is not None else None

    lessons_qs = Lesson.objects.visibles().filter(lectures__profil=profil)
    cours_qs = Cours.objects.visibles().filter(lectures__profil=profil)
    if cursus is not None:
        lessons_qs = lessons_qs.filter(cursus=cursus)
        cours_qs = cours_qs.filter(models.Q(cursus=cursus) | models.Q(cursus__isnull=True))

    lessons = (
        lessons_qs.select_related("subject__country")
        .order_by("-lectures__last_read_at")
    )
    cours = cours_qs.order_by("-lectures__last_read_at").distinct()

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
    if not has_access(request.user, exercise.lesson, profil_actif(request)):
        return Response({"error": "Abonnement requis pour cette épreuve."}, status=403)

    profil = profil_actif(request)
    fait = request.data.get("fait", True)
    gain = None
    if fait:
        _, cree = ExerciceFait.objects.get_or_create(profil=profil, exercise=exercise)
        # Les points de cet exercice, une seule fois pour toutes (voir quiz.xp.crediter_activite) : le décocher puis le
        # recocher ne rapporte rien de plus.
        if cree:
            gain = xp.crediter_activite(profil, SourceXP.EXERCICE, f"exercice:{exercise.pk}", xp.XP_EXERCICE)
    else:
        ExerciceFait.objects.filter(profil=profil, exercise=exercise).delete()
    return Response({
        "exercise_id": exercise.pk, "fait": bool(fait),
        "xp_gagne": gain.points if gain else 0, "xp_jour": xp.etat_du_jour(profil),
    })


def _marque_payload(marque):
    return {
        "cle": marque.cle,
        "compris": marque.compris,
        "signet": marque.signet,
        "note": marque.note,
        "updated_at": marque.updated_at,
    }


def _cible_etude(params):
    """Le document visé par cours=<id|slug> ou lesson=<id|slug>, ou None."""
    if params.get("cours"):
        return get_object_or_404(Cours.objects.visibles().par_slug_ou_id(params["cours"]))
    if params.get("lesson"):
        return get_object_or_404(Lesson.objects.visibles().par_slug_ou_id(params["lesson"]))
    return None


@api_view(["GET", "PUT"])
def etude_marques(request):
    """
    GET  ?cours=|?lesson= : les marques de l'élève sur ce document.
    PUT  {cours|lesson, cle, compris?, signet?, note?} : met à jour une section - seuls
    les champs présents changent, et la marque disparaît quand plus rien n'y reste.

    Réservé à qui a accès au document : une note posée sur une section qu'on ne peut pas
    lire n'a aucun sens (et ouvrirait un stockage libre à qui n'a rien payé).
    """
    source = request.query_params if request.method == "GET" else request.data
    cible = _cible_etude(source)
    if cible is None:
        return Response({"error": "Préciser cours ou lesson."}, status=400)
    if not has_access(request.user, cible, profil_actif(request)):
        return Response({"error": "Abonnement requis pour ce contenu."}, status=403)

    profil = profil_actif(request)
    if request.method == "GET":
        return Response([_marque_payload(m) for m in marques_du_document(profil, cible)])

    try:
        marque = enregistrer_marque(
            profil, cible, request.data.get("cle", ""),
            compris=request.data.get("compris"), signet=request.data.get("signet"), note=request.data.get("note"),
        )
    except MarqueInvalide as exc:
        return Response({"error": str(exc)}, status=400)
    if marque is None:
        return Response({"cle": request.data.get("cle"), "compris": False, "signet": False, "note": "", "updated_at": None})
    payload = _marque_payload(marque)
    # Une section de COURS déclarée comprise rapporte un peu, une fois pour toutes ; les sections d'épreuve n'en rapportent
    # pas (leurs exercices ont leur propre déclaration, voir marquer_exercice_fait).
    if marque.compris and request.data.get("compris") and isinstance(cible, Cours):
        gain = xp.crediter_activite(profil, SourceXP.COURS, f"cours:{cible.pk}:{marque.cle}", xp.XP_COURS_SECTION)
        if gain:
            payload["xp_gagne"] = gain.points
            payload["xp_jour"] = xp.etat_du_jour(profil)
    return Response(payload)


@api_view(["POST"])
def cours_lu(request, slug):
    """
    L'élève est arrivé au bout d'un cours (le lecteur le détecte : fin de l'article atteinte après un temps de lecture
    minimal). Rapporte XP_COURS_LU, une fois par cours pour toujours, dans le plafond d'activité du jour (voir
    quiz.xp.crediter_activite). Le serveur ne peut pas vérifier la lecture : c'est un geste déclaré, donc petit et plafonné.
    Réservé à qui a accès au cours, comme les marques d'étude.
    """
    cours = get_object_or_404(Cours.objects.visibles().par_slug_ou_id(slug))
    profil = profil_actif(request)
    if not has_access(request.user, cours, profil):
        return Response({"error": "Abonnement requis pour ce contenu."}, status=403)
    gain = xp.crediter_activite(profil, SourceXP.COURS, f"cours-lu:{cours.pk}", xp.XP_COURS_LU)
    return Response({"xp_gagne": gain.points if gain else 0, "xp_jour": xp.etat_du_jour(profil)})


@api_view(["GET"])
def etude_carnet(request):
    """
    Le carnet de l'élève : tout ce qu'il a mis de côté ou annoté, du plus récent au plus
    ancien, avec de quoi rouvrir la section exacte. Les "compris" seuls n'y figurent pas :
    c'est un suivi de progression, pas quelque chose qu'on relit.

    Une marque sur un document que l'élève ne peut plus lire (abonnement expiré) reste
    affichée : c'est SA note, la lui retirer serait la lui confisquer - la lecture, elle,
    reste gatée par le lecteur.
    """
    marques = (
        MarqueEtude.objects.filter(profil=profil_actif(request))
        .filter(models.Q(signet=True) | ~models.Q(note=""))
        .select_related("lesson__subject__country", "cours__subject__country")[:200]
    )
    carnet = []
    for marque in marques:
        doc = marque.cours or marque.lesson
        carnet.append({
            **_marque_payload(marque),
            "type": "cours" if marque.cours_id else "epreuve",
            "titre": doc.titre if marque.cours_id else doc.title,
            "slug": doc.slug,
            "country": doc.subject.country.code.lower(),
            "matiere": doc.subject.label,
        })
    return Response(carnet)
