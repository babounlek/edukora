"""
Inscrit sans paiement (audit du tunnel visiteur → abonné, rapport 17) : deux messages au compte qui a ouvert l'écran
d'abonnement et n'a ni payé ni déclaré de paiement, puis rien.

- le premier quand sa dernière ouverture de l'écran a entre 20 heures et 3 jours ;
- le second, et dernier, quand elle a entre 3 et 7 jours.

La relance d'un paiement non abouti (voir relances.services) part d'une transaction. Quand le paiement automatique est
coupé, ou quand l'élève referme l'écran avant de l'essayer, il n'y a pas de transaction : personne n'était relancé. Ici le
point de départ est l'évènement `abonnement_ouvert` (voir analytics.models), rattaché au compte connecté.

Comme sa sœur, c'est le suivi d'une démarche du compte, pas le rappel quotidien : il ne dépend pas du réglage « rappels »
(qui est coupé par défaut, et que seul un abonné a une raison d'activer), mais il exige une adresse confirmée. Il porte
son propre lien d'arrêt, que le compte n'a qu'à ouvrir pour ne plus rien recevoir à ce sujet (voir RefusRelance).

Jamais plus de deux messages par période de 30 jours, même si l'écran est rouvert dix fois : la trace d'envoi porte la
date de l'envoi, et les traces des 30 derniers jours décident (voir `_etape_due`). Rien n'y presse : pas de compte à
rebours, pas de « dernière chance », et il dit qu'aucun prélèvement n'est automatique.

Rien ne part quand :
- le compte a payé, déclaré un paiement ou a un accès en cours (services._a_deja_paye) ;
- une tentative de paiement est à reprendre (services.paiement_a_reprendre) : sa relance a la priorité, un seul sujet ;
- l'examen visé est passé, ou aucun examen n'est connu (ni dans l'évènement, ni sur le compte) ;
- le compte a ouvert le lien d'arrêt.

Par e-mail seulement pour l'instant.
"""
import logging
from datetime import date, timedelta

from django.conf import settings
from django.core import signing
from django.utils import timezone

from analytics.models import AnalyticsEvent, EventName
from catalog.models import Cursus
from edtech_cm import courriel
from quiz import textes
from subscriptions.models import DureeMode, Plan, ProductType
from users.models import User

from .fin_abonnement import _examen_passe
from .models import FamilleRelance, RefusRelance, RelanceEnvoyee, TypeRelance
from .services import _a_deja_paye, _envoyer_email, _salutation, _tracer, langue_du_compte, paiement_a_reprendre

logger = logging.getLogger("relances")

SALT_ARRET = "relances-desabonnement-inscrit-sans-paiement"

# Âge de la DERNIÈRE ouverture de l'écran d'abonnement. Vingt heures : le compte a eu sa soirée et sa matinée pour payer
# seul, et le tour du lendemain soir tombe dedans. Passé sept jours, le moment est passé : on n'écrit plus.
DELAI_PREMIER = timedelta(hours=20)
DELAI_DERNIER = timedelta(days=3)
DELAI_FIN = timedelta(days=7)
# Le plafond : deux messages par période de 30 jours, quel que soit le nombre d'ouvertures.
PERIODE_JOURS = 30
# Le dernier message ne suit jamais le premier de moins de deux jours (un ordonnanceur arrêté trois jours enverrait
# sinon les deux à une heure d'écart).
ECART_MIN_JOURS = 2

TYPES = (TypeRelance.INSCRIT_SANS_PAIEMENT_1, TypeRelance.INSCRIT_SANS_PAIEMENT_2)


# --------------------------------------------------------------------------- arrêt


def jeton_arret(user):
    return signing.dumps({"u": user.pk}, salt=SALT_ARRET)


def utilisateur_du_jeton_arret(jeton):
    """Le compte désigné par le jeton, ou None s'il est altéré. Sans expiration : un lien d'arrêt doit marcher pour
    toujours. Sel propre : le lien d'un rappel quotidien ne coupe pas ces messages, et inversement."""
    try:
        return User.objects.filter(pk=signing.loads(jeton, salt=SALT_ARRET)["u"]).first()
    except (signing.BadSignature, KeyError, TypeError):
        return None


def lien_arret(user):
    return f"{settings.FRONTEND_URL}/relances/desabonner-offre/{jeton_arret(user)}/"


def refuser(user):
    """Le compte ne veut plus de ces messages : définitif, et sans effet sur ses autres réglages."""
    RefusRelance.objects.get_or_create(user=user, famille=FamilleRelance.INSCRIT_SANS_PAIEMENT)


# --------------------------------------------------------------------------- ce que le message cite


def cursus_vise(user, proprietes):
    """L'examen de l'écran ouvert : `cursus_id` de l'évènement quand le frontend l'a joint, sinon l'examen déclaré du
    compte. None quand ni l'un ni l'autre n'est connu."""
    cursus_id = (proprietes or {}).get("cursus_id")
    if isinstance(cursus_id, int) and not isinstance(cursus_id, bool):
        cursus = Cursus.objects.filter(pk=cursus_id).select_related("country", "series").first()
        if cursus is not None:
            return cursus
    return user.cursus_prepare


def prix_du_mois(cursus):
    """Le prix d'un mois d'abonnement à cet examen, lu sur son plan au mois (voir subscriptions.models.Plan), ou None
    s'il n'y en a pas un seul sans ambiguïté - le message ne cite alors aucun prix. Hors campagne promotionnelle : une
    remise citée ici pourrait être terminée quand le message est lu ; l'écran d'abonnement, lui, affiche le prix du jour."""
    prix = {
        plan.tarif(campagne=None).prix
        for plan in Plan.objects.filter(
            cursus=cursus, product_type=ProductType.ABONNEMENT, duration_mode=DureeMode.MENSUEL, is_active=True,
        )
    }
    return prix.pop() if len(prix) == 1 else None


def _montant(prix):
    return courriel.montant_fcfa(prix)


def _profil_pour(user, cursus):
    """Le profil que l'écran d'abonnement présélectionne : celui qui prépare cet examen, sinon le premier du compte."""
    profils = list(user.profils.all())
    for profil in profils:
        if profil.cursus_prepare_id == cursus.pk:
            return profil
    return profils[0] if profils else None


_TEXTES = {
    textes.FR: {
        "ouverture_1": "Tu as ouvert la page d'abonnement à {site} ({cursus}) sans aller jusqu'au paiement. Au cas où cela "
                       "t'aide, voici ce que l'abonnement ouvre :",
        "ouverture_2": "Il y a quelques jours, tu as ouvert la page d'abonnement à {site} ({cursus}). C'est notre dernier "
                       "message à ce sujet.",
        "ouvre": "L'abonnement ouvre :",
        "contenu": [
            "les corrigés détaillés des épreuves ;",
            "les exercices d'application ;",
            "les quiz ;",
            "les épreuves inédites.",
        ],
        "prix": "Il coûte {montant} FCFA par mois.",
        "mois": "Tu choisis le nombre de mois et tu paies par Mobile Money (Orange Money ou MTN MoMo).",
        "sans_prelevement": "Aucun prélèvement automatique : l'accès s'arrête simplement à la fin des mois payés.",
        "bouton": "Revenir à la page d'abonnement",
        "raison": "Tu reçois ce message parce que tu as ouvert la page d'abonnement.",
        "arret": "Ne plus recevoir ces messages, en un clic",
        "titre_1": "Ce qu'ouvre l'abonnement",
        "titre_2": "Un dernier mot sur l'abonnement",
        "apercu": "Les corrigés détaillés, les exercices, les quiz et les épreuves inédites.",
        "sujet_1": "Ce qu'ouvre l'abonnement {site}",
        "sujet_2": "Un dernier mot sur l'abonnement {site}",
    },
    textes.EN: {
        "ouverture_1": "You opened the {site} subscription page ({cursus}) and stopped before paying. In case it helps, "
                       "here is what the subscription opens:",
        "ouverture_2": "A few days ago you opened the {site} subscription page ({cursus}). This is our last message about "
                       "it.",
        "ouvre": "The subscription opens:",
        "contenu": [
            "the detailed solutions to past papers;",
            "the practice exercises;",
            "the quizzes;",
            "the original mock papers.",
        ],
        "prix": "It costs {montant} FCFA per month.",
        "mois": "You choose the number of months and pay by Mobile Money (Orange Money or MTN MoMo).",
        "sans_prelevement": "No automatic charge: the access simply stops at the end of the months you paid for.",
        "bouton": "Back to the subscription page",
        "raison": "You receive this message because you opened the subscription page.",
        "arret": "Stop these messages in one click",
        "titre_1": "What the subscription opens",
        "titre_2": "A last word about the subscription",
        "apercu": "Detailed solutions, practice exercises, quizzes and original mock papers.",
        "sujet_1": "What the {site} subscription opens",
        "sujet_2": "A last word about the {site} subscription",
    },
}


def composer_relance_inscrit(user, cursus, type_):
    """(sujet, corps, html) dans la langue du compte. Les seuls faits cités sont en base : l'examen, le prix du mois
    quand il est connu. Aucune date, aucun compte à rebours."""
    langue = langue_du_compte(user)
    t = _TEXTES[langue]
    etape = 2 if type_ == TypeRelance.INSCRIT_SANS_PAIEMENT_2 else 1
    prix = prix_du_mois(cursus)
    profil = _profil_pour(user, cursus)
    lien = f"{settings.FRONTEND_URL}/abonnement?cursus={cursus.pk}"
    if profil is not None:
        lien += f"&profil={profil.pk}"

    message = courriel.Courriel(
        langue, salutation=_salutation(user, langue), titre=t[f"titre_{etape}"], apercu=t["apercu"],
        bouton=(t["bouton"], lien), raison=t["raison"], arret=(t["arret"], lien_arret(user)),
    )
    message.paragraphe(t[f"ouverture_{etape}"].format(site=settings.SITE_NAME, cursus=cursus))
    if etape == 2:
        message.paragraphe(t["ouvre"])
    message.liste(t["contenu"])
    if prix is not None:
        montant = _montant(prix)
        message.paragraphe(t["prix"].format(montant=montant), gras=f"{montant} FCFA")
    message.paragraphe(t["mois"]).paragraphe(t["sans_prelevement"])
    return t[f"sujet_{etape}"].format(site=settings.SITE_NAME), message.texte(), message.html()


# --------------------------------------------------------------------------- sélection


def _etape_due(age, traces, aujourdhui):
    """
    Le type du message à envoyer maintenant, ou None. `traces` : [(type, date d'envoi)] des deux messages partis à ce
    compte dans les 30 derniers jours.

    - le premier ne part que si RIEN n'est parti dans la période ;
    - le dernier ne part que si un seul message est parti dans la période, et que c'est un premier.
    Aucun message n'a donc jamais deux prédécesseurs dans ses 30 jours : deux au plus par période, où qu'on la fasse
    commencer, et quel que soit le nombre d'ouvertures de l'écran.
    """
    if DELAI_PREMIER <= age < DELAI_DERNIER:
        return TypeRelance.INSCRIT_SANS_PAIEMENT_1 if not traces else None
    if DELAI_DERNIER <= age <= DELAI_FIN:
        if len(traces) != 1:
            return None
        type_, jour = traces[0]
        if type_ == TypeRelance.INSCRIT_SANS_PAIEMENT_1 and (aujourdhui - jour).days >= ECART_MIN_JOURS:
            return TypeRelance.INSCRIT_SANS_PAIEMENT_2
    return None


def relances_inscrit_dues(maintenant=None):
    """[(compte, cursus, type, référence)] : les messages à envoyer maintenant.

    La référence est la date (locale) de l'envoi. Ni l'identifiant de l'évènement ni l'examen n'y figurent : rouvrir
    l'écran, ou changer d'examen, ne donne droit à aucun message de plus. La contrainte d'unicité empêche deux tours
    simultanés d'envoyer deux fois le même jour ; le plafond, lui, se lit sur les traces de la période."""
    maintenant = maintenant or timezone.now()
    aujourdhui = timezone.localtime(maintenant).date()

    # La dernière ouverture de chaque compte dans la fenêtre. Une ouverture plus récente que le premier délai repousse
    # tout : le compte est peut-être en train de payer.
    dernieres = {}
    evenements = (
        AnalyticsEvent.objects.filter(
            name=EventName.ABONNEMENT_OUVERT, user__isnull=False,
            created_at__gte=maintenant - DELAI_FIN, created_at__lte=maintenant,
            user__est_invite=False, user__is_active=True, user__email_verified=True, user__email__isnull=False,
        )
        .exclude(user__email="")
        .order_by("user_id", "-created_at")
        .values_list("user_id", "created_at", "properties")
    )
    for user_id, cree_le, proprietes in evenements:
        dernieres.setdefault(user_id, (cree_le, proprietes))
    candidats = {
        user_id: valeur for user_id, valeur in dernieres.items() if maintenant - valeur[0] >= DELAI_PREMIER
    }
    if not candidats:
        return []

    debut_periode = aujourdhui - timedelta(days=PERIODE_JOURS)
    traces = {}
    for user_id, type_, reference in RelanceEnvoyee.objects.filter(
        type__in=TYPES, user_id__in=candidats,
    ).values_list("user_id", "type", "reference"):
        try:
            jour = date.fromisoformat(reference)
        except ValueError:
            # Une référence illisible ne doit jamais ouvrir droit à un message de plus.
            jour = aujourdhui
        if jour > debut_periode:
            traces.setdefault(user_id, []).append((type_, jour))
    refus = set(
        RefusRelance.objects.filter(
            famille=FamilleRelance.INSCRIT_SANS_PAIEMENT, user_id__in=candidats,
        ).values_list("user_id", flat=True),
    )

    examens_passes = {}
    dues = []
    comptes = User.objects.filter(pk__in=candidats).select_related("cursus_prepare__country", "cursus_prepare__series")
    for user in comptes.order_by("pk"):
        if user.pk in refus:
            continue
        cree_le, proprietes = candidats[user.pk]
        type_ = _etape_due(maintenant - cree_le, traces.get(user.pk, []), aujourdhui)
        if type_ is None:
            continue
        cursus = cursus_vise(user, proprietes)
        if cursus is None or not cursus.country.actif:
            continue
        if _a_deja_paye(user) or paiement_a_reprendre(user, maintenant) is not None:
            continue
        if cursus.pk not in examens_passes:
            examens_passes[cursus.pk] = _examen_passe(cursus)
        if examens_passes[cursus.pk]:
            continue
        dues.append((user, cursus, type_, aujourdhui.isoformat()))
    return dues


def envoyer_relances_inscrit_sans_paiement(maintenant=None, *, dry_run=False):
    envoyes = 0
    for user, cursus, type_, reference in relances_inscrit_dues(maintenant):
        if dry_run:
            envoyes += 1
            continue
        try:
            message = composer_relance_inscrit(user, cursus, type_)
            if not _tracer(user, type_, reference):
                continue
            try:
                _envoyer_email(user, *message)
            except Exception:
                # Un envoi raté ne doit pas rester marqué « fait » : le tour suivant le retentera, dans sa fenêtre.
                RelanceEnvoyee.objects.filter(user=user, type=type_, reference=reference).delete()
                raise
            envoyes += 1
        except Exception:
            logger.exception("Relance d'inscrit sans paiement non envoyée au compte %s", user.pk)
    return envoyes
