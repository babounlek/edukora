"""
L'avis qu'un élève ou un parent laisse dans l'application (audit de l'accueil du 2026-11-15, R8 : preuve sociale réelle
ou absente, jamais fabriquée).

GET  /catalog/avis/  -> à qui l'application peut encore demander un avis, et ce qui serait affiché sous son texte.
POST /catalog/avis/  -> enregistre l'avis, en brouillon : rien n'est public tant qu'un admin ne l'a pas relu et publié.

Règles, dans l'ordre où elles comptent :

- **Jamais d'office.** L'avis n'est publiable que si son auteur a coché la case de consentement (`consentement_at`).
  Sans elle, il est gardé pour l'équipe et `Temoignage.clean` refuse sa publication.
- **Le moins possible sur un mineur.** Un prénom et l'examen préparé, rien d'autre : pas de nom, de photo,
  d'établissement, de ville. Le prénom est filtré (lettres seulement) pour qu'un numéro ou une adresse n'y entre pas ;
  la relecture dans l'admin reste la vraie barrière.
- **Après usage réel.** On ne demande qu'à partir de SEUIL_QUIZ quiz terminés : un avis d'avant l'usage ne dit rien.
- **Une seule fois.** Un avis par profil et par rôle (contrainte en base) ; l'application ne redemande pas.
- **Retirable.** Supprimer le profil dépublie son avis (voir _depublier_les_avis) : l'accord s'en va avec lui.
"""
import re

from django.db import IntegrityError, transaction
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from users.profils import profil_actif

from .libelles import libelle_cursus
from .models import ORIGINES_DANS_L_APPLICATION, Langue, OrigineTemoignage, Temoignage

# Nombre de quiz terminés à partir duquel on demande : le troisième, quand l'élève a de quoi juger.
SEUIL_QUIZ = 3
LONGUEUR_MAX_PRENOM = 30
LONGUEUR_MAX_CONTENU = 600

# Un prénom, simple ou composé : des lettres, séparées par une espace, un trait d'union ou une apostrophe. Ni chiffre
# (un numéro de téléphone), ni « @ », ni point (une adresse, un identifiant).
_PRENOM_RE = re.compile(r"^[^\W\d_]+(?:[ '’\-][^\W\d_]+)*$")

# Ce qui s'affiche sous l'avis d'un parent, dans la langue de l'avis.
_MENTION_PARENT = {Langue.FR: "Parent d'élève", Langue.EN: "Parent of a student"}
_AUTEUR_PAR_DEFAUT = {
    OrigineTemoignage.ELEVE: {Langue.FR: "Élève", Langue.EN: "Student"},
    OrigineTemoignage.PARENT: {Langue.FR: "Parent", Langue.EN: "Parent"},
}


def _quiz_termines(profils):
    # Import local : quiz dépend déjà de catalog au chargement des modèles.
    from quiz.models import QuizSession

    return QuizSession.objects.filter(profil__in=profils, completed_at__isnull=False).count()


def _profil_du_parent(user):
    """Le profil qui porte l'avis du titulaire du compte : le premier, stable d'une visite à l'autre."""
    return user.profils.order_by("id").first()


def _etat(request):
    """
    Ce que l'application peut encore demander à cette personne.

    - élève : le profil actif a terminé SEUIL_QUIZ quiz et n'a pas déjà donné son avis ;
    - parent : le compte, tous profils confondus, a terminé SEUIL_QUIZ quiz et n'a pas déjà donné le sien.

    Un compte invité (essai gratuit sans inscription, voir users.models.User.est_invite) n'est jamais sollicité : il n'a
    pas d'identité, et son compte disparaît.
    """
    user = request.user
    profil = profil_actif(request)
    if profil is None or user.est_invite:
        return {"eleve": False, "parent": False, "prenom": "", "examen": ""}
    deja = set(
        Temoignage.objects.filter(profil__compte=user, origine__in=ORIGINES_DANS_L_APPLICATION)
        .values_list("profil_id", "origine")
    )
    parent = _profil_du_parent(user)
    return {
        "eleve": (profil.id, OrigineTemoignage.ELEVE) not in deja and _quiz_termines([profil]) >= SEUIL_QUIZ,
        "parent": (
            parent is not None
            and (parent.id, OrigineTemoignage.PARENT) not in deja
            and _quiz_termines(user.profils.all()) >= SEUIL_QUIZ
        ),
        "prenom": profil.prenom or "",
        "examen": libelle_cursus([profil.cursus_prepare]) if profil.cursus_prepare else "",
    }


def _prenom_propre(brut):
    """Le prénom tel qu'il sera affiché, ou None s'il n'en est pas un (voir _PRENOM_RE)."""
    prenom = " ".join(str(brut or "").split())[:LONGUEUR_MAX_PRENOM]
    return prenom if prenom and _PRENOM_RE.match(prenom) else None


def _refus(message, code=status.HTTP_400_BAD_REQUEST):
    return Response({"detail": message}, status=code)


@api_view(["GET", "POST"])
@permission_classes([permissions.IsAuthenticated])
def avis_view(request):
    etat = _etat(request)
    if request.method == "GET":
        return Response(etat)

    origine = str(request.data.get("origine") or "").upper()
    if origine not in (OrigineTemoignage.ELEVE, OrigineTemoignage.PARENT):
        return _refus("Origine inconnue.")
    if not etat["eleve" if origine == OrigineTemoignage.ELEVE else "parent"]:
        # Déjà donné, pas encore assez de quiz, ou compte invité : dans tous les cas, rien à enregistrer.
        return _refus("Aucun avis n'est attendu pour ce compte.", status.HTTP_409_CONFLICT)

    try:
        note = int(request.data.get("note"))
    except (TypeError, ValueError):
        note = 0
    if not 1 <= note <= 5:
        return _refus("La note doit être comprise entre 1 et 5.")

    contenu = str(request.data.get("contenu") or "").strip()
    if len(contenu) > LONGUEUR_MAX_CONTENU:
        return _refus(f"L'avis ne doit pas dépasser {LONGUEUR_MAX_CONTENU} caractères.")

    consentement = request.data.get("consentement") is True
    prenom = _prenom_propre(request.data.get("prenom"))
    if consentement and prenom is None:
        # Publier demande un prénom à afficher ; sans accord, l'avis reste interne et s'en passe.
        return _refus("Indique ton prénom, en lettres seulement.")

    langue = str(request.data.get("langue") or "").lower()
    if langue not in Langue.values:
        langue = request.user.langue if request.user.langue in Langue.values else Langue.FR

    eleve = origine == OrigineTemoignage.ELEVE
    profil = profil_actif(request) if eleve else _profil_du_parent(request.user)
    cursus = profil_actif(request).cursus_prepare
    try:
        with transaction.atomic():
            Temoignage.objects.create(
                origine=origine, profil=profil, cursus=cursus, langue=langue,
                consentement_at=timezone.now() if consentement else None,
                auteur_nom=prenom or _AUTEUR_PAR_DEFAUT[origine][langue],
                auteur_description=(etat["examen"] if eleve else _MENTION_PARENT[langue])[:150],
                contenu=contenu, note=note,
            )
    except IntegrityError:
        # Deux envois en même temps (double toucher) : le premier a gagné, voir la contrainte du modèle.
        return _refus("Aucun avis n'est attendu pour ce compte.", status.HTTP_409_CONFLICT)
    return Response({"enregistre": True}, status=status.HTTP_201_CREATED)


@receiver(pre_delete, sender="users.Profil")
def _depublier_les_avis(sender, instance, **kwargs):
    """
    Le profil s'en va (compte supprimé, enfant retiré d'un compte famille) : son avis n'est plus public. La ligne reste,
    détachée du profil (SET_NULL), pour que l'équipe garde la note ; le texte publié portait un prénom, et l'accord de
    l'afficher part avec son auteur.
    """
    Temoignage.objects.filter(profil=instance, est_publie=True).update(est_publie=False)
