"""
Endpoints DRF de l'outil Fiches (répétiteur) - fonctions plates, pas de serializer,
même style que quiz.views/inedit.views. `create_fiche` est le seul point réellement
gaté par has_access_fiches (voir sa docstring) - les sous-endpoints (détail,
téléchargement) ne re-vérifient que l'ownership, même compromis que
inedit.views.tentative_detail (voir sa docstring de module).
"""

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from rest_framework.decorators import api_view
from rest_framework.response import Response

from access.services import has_access_fiches
from catalog.models import Cursus, Subject, Tag
from catalog.serializers import CursusSerializer
from subscriptions.models import InscriptionRepetiteur

from .models import FicheGeneree
from .pdf import queue_fiche_pdf_generation
from .services import generer_fiche, themes_eligibles


def _cursus_display(cursus):
    return f"{cursus.display_examen()} - Série {cursus.series.code}" if cursus.series else cursus.display_examen()


def _fiche_payload(fiche):
    return {
        "id": fiche.id,
        "titre": fiche.titre,
        "cursus": fiche.cursus_id,
        "cursus_display": _cursus_display(fiche.cursus),
        "subject_label": fiche.subject.label,
        "themes": [t.name for t in fiche.themes.all()],
        "difficulte": fiche.difficulte,
        "nombre_questions": fiche.nombre_questions,
        "statut": fiche.statut,
        "sujet_pdf_disponible": bool(fiche.sujet_pdf),
        "corrige_pdf_disponible": bool(fiche.corrige_pdf),
        "created_at": fiche.created_at,
    }


@api_view(["GET"])
def list_my_inscriptions_repetiteur(request):
    """Mes inscriptions à l'add-on Fiches - même rôle que
    inedit.views.list_my_inscriptions_inedites, nécessaire au frontend pour savoir, par
    cursus, s'il faut proposer le formulaire ou une mise en avant de l'add-on avant même
    de le remplir (voir create_fiche pour le point réellement gaté)."""
    inscriptions = (
        InscriptionRepetiteur.objects.filter(user=request.user)
        .select_related("cursus__series", "cursus__country")
    )
    return Response([
        {
            "id": inscription.id,
            "cursus": CursusSerializer(inscription.cursus).data,
            "expires_at": inscription.expires_at,
            "is_active": inscription.is_active,
        }
        for inscription in inscriptions
    ])


@api_view(["GET"])
def eligibilite(request):
    """Compétences disponibles (avec compteur) pour un (cursus, matière) - jamais gaté
    par has_access_fiches : alimente le formulaire de configuration, qui doit rester
    explorable avant achat (même logique que le catalogue lui-même, gaté seulement à
    l'action). Voir fiches.services.themes_eligibles pour le garde-fou anti-fiche-vide."""
    cursus_id = request.GET.get("cursus")
    subject_id = request.GET.get("subject")
    if not cursus_id or not subject_id:
        return Response({"error": "cursus et subject sont requis."}, status=400)
    cursus = get_object_or_404(Cursus, pk=cursus_id)
    subject = get_object_or_404(Subject, pk=subject_id)
    return Response(themes_eligibles(cursus, subject))


@api_view(["POST"])
def create_fiche(request):
    """Crée une FicheGeneree pour l'utilisateur connecté et lance la génération PDF en
    arrière-plan - gating par has_access_fiches (add-on Fiches actif sur ce cursus)."""
    cursus = get_object_or_404(Cursus.objects.select_related("country"), pk=request.data.get("cursus"))
    if not cursus.country.actif:
        return Response({"error": "Ce cursus n'est pas disponible."}, status=404)
    if not has_access_fiches(request.user, cursus):
        return Response({"error": "Add-on Fiches requis pour ce cursus."}, status=403)

    subject = get_object_or_404(Subject, pk=request.data.get("subject"))
    themes = list(Tag.objects.filter(pk__in=request.data.get("themes") or []))
    if not themes:
        return Response({"error": "Au moins une compétence est requise."}, status=400)

    difficulte = request.data.get("difficulte") or ""
    try:
        n = int(request.data.get("n") or 10)
    except (TypeError, ValueError):
        return Response({"error": "n doit être un entier."}, status=400)
    if n < 1:
        return Response({"error": "n doit être au moins 1."}, status=400)

    titre = (request.data.get("titre") or "").strip() or f"Fiche {subject.label}"

    try:
        fiche = generer_fiche(
            user=request.user, cursus=cursus, subject=subject, themes=themes,
            difficulte=difficulte, n=n, titre=titre,
        )
    except ValueError as exc:
        return Response({"error": str(exc)}, status=404)

    queue_fiche_pdf_generation(fiche.id)
    return Response(_fiche_payload(fiche), status=201)


@api_view(["GET"])
def list_my_fiches(request):
    fiches = (
        FicheGeneree.objects.filter(owner=request.user)
        .select_related("cursus__series", "cursus__country", "subject")
        .prefetch_related("themes")
    )
    return Response([_fiche_payload(fiche) for fiche in fiches])


@api_view(["GET"])
def fiche_detail(request, fiche_id):
    """Détail/poll d'une fiche - gaté par ownership seulement (pas has_access_fiches à
    nouveau) : une fiche déjà générée reste consultable même si l'add-on a expiré
    depuis, même principe que inedit.views.tentative_detail (voir sa docstring)."""
    fiche = get_object_or_404(
        FicheGeneree.objects.select_related("cursus__series", "cursus__country", "subject").prefetch_related("themes"),
        pk=fiche_id, owner=request.user,
    )
    return Response(_fiche_payload(fiche))


@api_view(["GET"])
def download_sujet_pdf(request, fiche_id):
    fiche = get_object_or_404(FicheGeneree, pk=fiche_id, owner=request.user)
    if not fiche.sujet_pdf:
        return Response({"error": "PDF pas encore généré."}, status=404)
    return FileResponse(
        fiche.sujet_pdf.open("rb"), as_attachment=False,
        filename=f"{slugify(fiche.titre)}-sujet.pdf", content_type="application/pdf",
    )


@api_view(["GET"])
def download_corrige_pdf(request, fiche_id):
    fiche = get_object_or_404(FicheGeneree, pk=fiche_id, owner=request.user)
    if not fiche.corrige_pdf:
        return Response({"error": "PDF pas encore généré."}, status=404)
    return FileResponse(
        fiche.corrige_pdf.open("rb"), as_attachment=False,
        filename=f"{slugify(fiche.titre)}-corrige.pdf", content_type="application/pdf",
    )
