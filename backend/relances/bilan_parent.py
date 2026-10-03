"""
Le bilan de la semaine, envoyé au PARENT (le titulaire du compte) chaque dimanche soir.

C'est ce qui lui montre ce qu'il paie : combien de jours son enfant a révisé, ce qu'il a consolidé.
Il se lit sur le bilan de période déjà calculé pour l'élève (voir quiz.bilan), ramené à sept jours -
aucun chiffre de plus à tenir à jour, et le parent ne peut pas voir autre chose que ce que voit l'élève.

Trois règles de ton, parce qu'un parent qui reçoit un reproche en fait un à son enfant :
- seulement des faits, jamais un jugement ni une comparaison avec d'autres élèves ;
- une semaine sans révision est dite simplement, avec la façon la plus courte de reprendre ;
- un seul message par semaine, qui regroupe tous les profils du compte (un compte famille n'envoie
  pas un e-mail par enfant).

Sur le même canal que les autres relances (e-mail confirmé, désabonnement en un clic, trace
RelanceEnvoyee pour ne jamais partir deux fois) ; WhatsApp s'y branchera quand son modèle de message
sera approuvé par Meta (voir relances.services).
"""

import logging
from datetime import timedelta

from django.conf import settings
from django.core import signing
from django.utils import timezone

from quiz.bilan import bilan_de_periode
from quiz.models import JourXP
from quiz.serie import serie_de_jours
from subscriptions.models import Subscription
from users.models import User

from .models import RelanceEnvoyee, TypeRelance
from .services import _envoyer_email, _salutation, _tracer

logger = logging.getLogger("relances")

SALT_BILAN = "relances-desabonnement-bilan"
JOURS_BILAN = 7
# Le bilan part le dimanche (jour 6 de weekday()) en fin d'après-midi : la semaine est finie, le
# parent est disponible, et l'enfant a encore la soirée pour reprendre si le bilan le motive.
JOUR_ENVOI = 6
HEURE_DEBUT_BILAN = 17
HEURE_FIN_BILAN = 21


# --------------------------------------------------------------------------- désabonnement


def jeton_desabonnement_bilan(user):
    return signing.dumps({"u": user.pk}, salt=SALT_BILAN)


def utilisateur_du_jeton_bilan(jeton):
    """Le titulaire désigné par le jeton, ou None s'il est altéré. Sans expiration : un lien de
    désabonnement doit marcher pour toujours."""
    try:
        return User.objects.filter(pk=signing.loads(jeton, salt=SALT_BILAN)["u"]).first()
    except (signing.BadSignature, KeyError):
        return None


def lien_desabonnement_bilan(user):
    return f"{settings.FRONTEND_URL}/relances/desabonner-bilan/{jeton_desabonnement_bilan(user)}/"


# --------------------------------------------------------------------------- contenu


def reference_semaine(maintenant=None):
    """Identifiant de la semaine ISO locale (« 2026-W40 ») : un bilan par compte et par semaine."""
    jour = timezone.localtime(maintenant).date() if maintenant else timezone.localdate()
    annee, semaine, _ = jour.isocalendar()
    return f"{annee}-W{semaine:02d}"


def _pluriel(n, singulier, pluriel=None):
    return f"{n} {singulier if n <= 1 else (pluriel or singulier + 's')}"


def _prenom_profil(profil, user):
    nom = (profil.prenom or user.full_name or user.pseudo or "").strip()
    return nom.split()[0] if nom else "Ton enfant"


def bilan_du_profil(profil, maintenant=None):
    """Le bilan des 7 derniers jours d'un profil abonné, ou None s'il n'a aucun abonnement actif.
    Tout vient de quiz.bilan et quiz.xp : rien n'est recalculé ici."""
    aujourdhui = timezone.localtime(maintenant).date() if maintenant else timezone.localdate()
    abonnement = (
        Subscription.objects.filter(profil=profil, expires_at__gt=maintenant or timezone.now())
        .select_related("cursus").order_by("-expires_at").first()
    )
    if abonnement is None:
        return None
    bilan = bilan_de_periode(profil, abonnement.cursus, aujourdhui=aujourdhui, jours=JOURS_BILAN)
    if bilan is None:
        return None
    xp = sum(
        JourXP.objects.filter(profil=profil, jour__gt=aujourdhui - timedelta(days=JOURS_BILAN), jour__lte=aujourdhui)
        .values_list("xp", flat=True),
    )
    return {**bilan, "xp": xp, "serie": serie_de_jours(profil, aujourdhui)["jours"]}


def _bloc_profil(prenom, bilan):
    if not bilan["a_de_l_activite"] and bilan["xp"] == 0:
        return [
            f"■ {prenom}",
            f"  {prenom} n'a pas révisé cette semaine. Une séance du jour dure environ 25 minutes : "
            "le plan est prêt dans l'application.",
        ]
    faits = [
        f"{bilan['jours_actifs']} jour{'s' if bilan['jours_actifs'] > 1 else ''} de révision sur 7",
        _pluriel(bilan["seances"], "séance"),
        _pluriel(bilan["questions"], "question")
        + (f" ({bilan['taux_reussite']} % de réussite)" if bilan["taux_reussite"] is not None else ""),
    ]
    if bilan["xp"]:
        faits.append(f"{bilan['xp']} XP")
    lignes = [f"■ {prenom}", "  " + ", ".join(faits) + "."]
    if bilan["themes_consolides"]:
        citations = ", ".join(f"{t['theme']} ({t['subject_label']})" for t in bilan["themes_consolides"])
        lignes.append(f"  Thèmes consolidés : {citations}.")
    if bilan["serie"] >= 2:
        lignes.append(f"  Série en cours : {bilan['serie']} jours de suite.")
    return lignes


def composer_bilan_parent(user, maintenant=None):
    """(sujet, corps) du bilan de la semaine pour tous les profils abonnés du compte, ou None s'il
    n'y en a aucun - un compte sans abonnement actif n'a rien à raconter."""
    blocs = []
    prenoms = []
    for profil in user.profils.all():
        bilan = bilan_du_profil(profil, maintenant)
        if bilan is None:
            continue
        prenom = _prenom_profil(profil, user)
        prenoms.append(prenom)
        blocs.append(_bloc_profil(prenom, bilan))
    if not blocs:
        return None

    lignes = [_salutation(user), "", "Voici la semaine qui vient de s'écouler :", ""]
    for bloc in blocs:
        lignes += bloc + [""]
    lignes += [
        f"Ouvrir {settings.SITE_NAME} : {settings.FRONTEND_URL}",
        "",
        "Tu reçois ce message parce que tu as activé le bilan de la semaine.",
        f"L'arrêter en un clic : {lien_desabonnement_bilan(user)}",
    ]
    sujet = f"Bilan de la semaine de {prenoms[0]}" if len(prenoms) == 1 else "Bilan de la semaine de tes enfants"
    return sujet, "\n".join(lignes)


# --------------------------------------------------------------------------- envoi


def destinataires_bilan_parent(maintenant=None):
    """Titulaires qui ont demandé le bilan, avec une adresse confirmée, au moins un abonnement
    actif, et qui ne l'ont pas déjà reçu cette semaine."""
    maintenant = maintenant or timezone.now()
    deja = RelanceEnvoyee.objects.filter(
        type=TypeRelance.BILAN_PARENT, reference=reference_semaine(maintenant),
    ).values("user_id")
    return (
        User.objects.filter(
            bilan_parent_actif=True, email_verified=True, email__isnull=False,
            subscriptions__expires_at__gt=maintenant,
        )
        .exclude(pk__in=deja)
        .distinct()
    )


def envoyer_bilans_parent(maintenant=None, *, dry_run=False):
    maintenant = maintenant or timezone.now()
    reference = reference_semaine(maintenant)
    envoyes = 0
    for user in destinataires_bilan_parent(maintenant):
        if dry_run:
            envoyes += 1
            continue
        try:
            message = composer_bilan_parent(user, maintenant)
            if message is None:
                continue
            if not _tracer(user, TypeRelance.BILAN_PARENT, reference):
                continue
            try:
                _envoyer_email(user, *message)
            except Exception:
                RelanceEnvoyee.objects.filter(user=user, type=TypeRelance.BILAN_PARENT, reference=reference).delete()
                raise
            envoyes += 1
        except Exception:
            logger.exception("Bilan parent non envoyé au titulaire %s", user.pk)
    return envoyes
