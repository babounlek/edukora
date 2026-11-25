from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from access.carnet import entree_note_libre
from users.profils import profil_actif

from . import services
from .gratuites import cle_de_tri


def _cursus(request):
    valeur = request.query_params.get("cursus", "")
    return int(valeur) if valeur.isdigit() else None


def _qui(request):
    """(user, profil) : un visiteur lit les fiches gratuites, il n'a ni profil ni abonnement."""
    if not request.user.is_authenticated:
        return None, None
    return request.user, profil_actif(request)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def matieres(request):
    """GET ?cursus=<id> : les matières qui ont des fiches pour cet examen, avec leur nombre (et combien sont gratuites)."""
    cursus_id = _cursus(request)
    if cursus_id is None:
        return Response({"error": "Paramètre cursus requis."}, status=400)
    user, profil = _qui(request)
    lignes = (
        services.visibles().filter(cursus=cursus_id)
        .values("subject_id", "subject__label", "subject__code")
        .annotate(total=Count("pk", distinct=True), gratuites=Count("pk", filter=Q(gratuit=True), distinct=True))
        .order_by("subject__label")
    )
    return Response({
        "abonne": services.a_l_abonnement(user, profil, cursus_id),
        "matieres": [
            {"matiere_id": l["subject_id"], "matiere": l["subject__label"], "matiere_code": l["subject__code"],
             "total": l["total"], "gratuites": l["gratuites"]}
            for l in lignes
        ],
    })


APERCU_MAX = 3


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def apercu(request):
    """
    GET ?pays=<code>&cursus=<id facultatif> : quelques fiches GRATUITES, définition comprise, pour les montrer sur l'accueil
    et dans Mes notes à qui n'est pas abonné. {total, fiches}. Avec un examen, seulement les siennes (jamais celles d'un
    autre examen) ; sans examen déclaré, celles du pays. Rien tant qu'aucune fiche n'est publiée.
    """
    pays = request.query_params.get("pays", "")
    if not pays:
        return Response({"error": "Paramètre pays requis."}, status=400)
    qs = services.visibles().filter(subject__country__code__iexact=pays)
    cursus_id = _cursus(request)
    if cursus_id is not None:
        qs = qs.filter(cursus=cursus_id)
    total = qs.distinct().count()
    fiches = []
    gratuites = qs.filter(gratuit=True).distinct().select_related("subject").prefetch_related("cursus")
    for memo in sorted(gratuites, key=lambda m: cle_de_tri(m, cursus_id))[:APERCU_MAX]:
        examens = list(memo.cursus.all())
        vise = next((c for c in examens if c.pk == cursus_id), examens[0] if examens else None)
        if vise is None:
            continue
        fiches.append({
            **services.entree(memo, lisible=True, gardee=False, cursus_id=vise.pk),
            "matiere": memo.subject.label,
            "matiere_code": memo.subject.code,
            "cursus_id": vise.pk,
            "examen": str(vise),
        })
    return Response({"total": total, "fiches": fiches})


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def liste(request):
    """
    GET ?cursus=<id>&matiere=<id> : les fiches d'une matière pour cet examen. Sans abonnement, seules les gratuites
    donnent leur définition ; les autres montrent le terme et les sessions où il est tombé.
    """
    cursus_id = _cursus(request)
    matiere = request.query_params.get("matiere", "")
    if cursus_id is None or not matiere.isdigit():
        return Response({"error": "Paramètres cursus et matiere requis."}, status=400)
    user, profil = _qui(request)
    abonne = services.a_l_abonnement(user, profil, cursus_id)
    memos = sorted(
        services.visibles().filter(cursus=cursus_id, subject_id=int(matiere)).distinct(),
        key=lambda m: cle_de_tri(m, cursus_id),
    )
    deja = services.gardees(profil, memos)
    return Response({
        "abonne": abonne,
        "fiches": [services.entree(m, lisible=abonne or m.gratuit, gardee=m.pk in deja, cursus_id=cursus_id) for m in memos],
    })


@api_view(["POST"])
def garder(request, pk):
    """POST : garde la fiche dans les notes de l'élève (voir services.garder_dans_les_notes). 403 si elle lui est verrouillée."""
    memo = get_object_or_404(services.visibles(), pk=pk)
    profil = profil_actif(request)
    cursus_ids = set(memo.cursus.values_list("pk", flat=True))
    from access.services import bulk_active_subscription_cursus_ids

    if not memo.gratuit and not (cursus_ids & bulk_active_subscription_cursus_ids(request.user, profil)):
        return Response({"error": "Cette fiche demande l'abonnement."}, status=403)
    note, creee = services.garder_dans_les_notes(profil, memo)
    return Response(entree_note_libre(note), status=201 if creee else 200)
