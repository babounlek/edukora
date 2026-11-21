"""
Fin d'abonnement (audit des accueils du 2026-11-21, A1 ; audit 14, F1) : deux messages au compte qui a payé, puis rien.

- le premier trois jours avant la fin de l'accès : la date, le lien direct pour prolonger le bon profil au bon examen ;
- le second, et dernier, le jour où l'accès se termine.

L'abonnement se paie au mois, sans prélèvement automatique : chaque fin de période est une nouvelle vente, et rien ne la
préparait - la date de fin n'était écrite que dans le menu du compte. Après ces deux messages, l'application prend le
relais (voir AccueilDecouverte côté frontend : la date de fin, ce que l'élève retrouve, « Me réabonner »).

Comme la relance d'un paiement non abouti (voir relances.services), c'est le suivi d'un accès PAYÉ, pas de la publicité :
il ne dépend pas du réglage « rappels » de l'élève, mais il exige une adresse confirmée, et il part au compte, donc au
payeur. Rien n'y presse : pas de compte à rebours, pas de prix, et il dit que rien n'est prélevé.

Rien ne part quand :
- l'examen est passé (prolonger n'aurait pas de sens) ;
- un paiement par transfert est en cours de vérification pour ce profil et cet examen (il a déjà payé) ;
- l'accès a été prolongé entre-temps (sa date de fin n'est plus dans la fenêtre).

Par e-mail seulement pour l'instant. Le canal WhatsApp se brancherait ici quand ses modèles seront approuvés par Meta.
"""
import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from catalog.models import ExamSession
from payments.models import ManualPayment, ManualPaymentStatus
from quiz import textes
from quiz.models import SeanceJournaliere, StatutSeance
from subscriptions.models import Subscription

from .models import RelanceEnvoyee, TypeRelance
from .services import _envoyer_email, _prenom, _salutation, _tracer, langue_du_compte

logger = logging.getLogger("relances")

# Jours entre aujourd'hui et le jour où l'accès se termine (dates locales). Le premier message a deux jours pour partir :
# si l'ordonnanceur a manqué le soir de J-3, il part à J-2, pas plus tard. Le second ne part que le jour même : « se
# termine aujourd'hui » reçu le lendemain serait faux.
FENETRES = (
    (TypeRelance.FIN_ABONNEMENT_1, 2, 3),
    (TypeRelance.FIN_ABONNEMENT_2, 0, 0),
)
JOURS_AVANT_MAX = max(fin for _type, _debut, fin in FENETRES)

_MOIS = {
    textes.FR: ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre",
                "novembre", "décembre"],
    textes.EN: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                "November", "December"],
}


def _date_en_clair(jour, langue):
    """« 13 décembre 2026 » / « 13 December 2026 », sans dépendre de la langue active du processus."""
    return f"{jour.day} {_MOIS[langue][jour.month - 1]} {jour.year}"


def reference_de(abonnement):
    """Ce à propos de quoi le message part : CET accès, à CETTE date de fin. Un accès prolongé change de date de fin, donc
    de référence : sa prochaine échéance aura de nouveau ses deux messages."""
    return f"{abonnement.pk}:{timezone.localtime(abonnement.expires_at).date().isoformat()}"


def composer_relance_fin_abonnement(abonnement, type_):
    """(sujet, corps) en texte brut, dans la langue du compte. Les seuls faits cités sont en base : la date de fin, l'examen,
    le prénom du profil, le nombre de séances terminées."""
    user, profil, cursus = abonnement.user, abonnement.profil, abonnement.cursus
    langue = langue_du_compte(user)
    anglais = langue == textes.EN
    date = _date_en_clair(timezone.localtime(abonnement.expires_at).date(), langue)
    dernier = type_ == TypeRelance.FIN_ABONNEMENT_2
    prenom = (getattr(profil, "prenom", "") or "").strip()
    # Le profil est celui du titulaire lui-même (même prénom que la salutation) : « Ton accès », pas « L'accès de Awa »
    # écrit à Awa. Un parent qui paie pour son enfant lit le prénom de l'enfant.
    if prenom.casefold() == _prenom(user).casefold():
        prenom = ""
    seances = SeanceJournaliere.objects.filter(profil=profil, cursus=cursus, statut=StatutSeance.TERMINEE).count()
    lien = f"{settings.FRONTEND_URL}/abonnement?cursus={cursus.pk}&profil={profil.pk}"

    if anglais:
        qui = f"{prenom}'s access" if prenom else "Your access"
        echeance = (
            f"{qui} to {settings.SITE_NAME} ({cursus}) ends today, {date}." if dernier
            else f"{qui} to {settings.SITE_NAME} ({cursus}) ends on {date}."
        )
        lignes = [_salutation(user, langue), "", echeance]
        if seances:
            lignes.append(
                f"{seances} session{'s' if seances > 1 else ''} completed so far. Progress, revision topics and mistakes "
                "to redo are kept, and are there again as soon as the access is extended."
            )
        lignes += [
            "",
            f"Extend the access: {lien}",
            "You choose the number of months and pay by Mobile Money (Orange Money or MTN MoMo).",
            "",
            "Nothing is charged automatically: if you do nothing, the access simply stops on that date.",
        ]
        if dernier:
            lignes.append("This is our last message about it.")
        lignes += ["", "A question? Just reply to this message."]
        sujet = (
            f"Last day of your {settings.SITE_NAME} access" if dernier
            else f"Your {settings.SITE_NAME} access ends on {date}"
        )
        return sujet, "\n".join(lignes)

    # « d'Awa », « de Guyguy ».
    de = "d'" if prenom[:1].casefold() in "aeiouyhàâéèêëîïôöùûü" else "de "
    qui = f"L'accès {de}{prenom}" if prenom else "Ton accès"
    echeance = (
        f"{qui} à {settings.SITE_NAME} ({cursus}) se termine aujourd'hui, le {date}." if dernier
        else f"{qui} à {settings.SITE_NAME} ({cursus}) se termine le {date}."
    )
    lignes = [_salutation(user, langue), "", echeance]
    if seances:
        lignes.append(
            f"{seances} séance{'s' if seances > 1 else ''} terminée{'s' if seances > 1 else ''} jusqu'ici. La progression, "
            "les thèmes en révision et les erreurs à refaire sont gardés, et reviennent dès que l'accès est prolongé."
        )
    lignes += [
        "",
        f"Prolonger l'accès : {lien}",
        "Tu choisis le nombre de mois et tu paies par Mobile Money (Orange Money ou MTN MoMo).",
        "",
        "Rien n'est prélevé automatiquement : sans action de ta part, l'accès s'arrête simplement à cette date.",
    ]
    if dernier:
        lignes.append("C'est notre dernier message à ce sujet.")
    lignes += ["", "Une question ? Réponds simplement à ce message."]
    sujet = (
        f"Dernier jour de ton accès {settings.SITE_NAME}" if dernier
        else f"Ton accès {settings.SITE_NAME} se termine le {date}"
    )
    return sujet, "\n".join(lignes)


def _examen_passe(cursus):
    compte = ExamSession.compte_a_rebours_pour(cursus)
    return bool(compte) and compte["jours_restants"] < 0


def relances_fin_abonnement_dues(maintenant=None):
    """[(abonnement, type, référence)] : les messages de fin d'abonnement à envoyer maintenant."""
    maintenant = maintenant or timezone.now()
    aujourdhui = timezone.localtime(maintenant).date()
    candidats = (
        Subscription.objects.filter(
            # Une marge d'un jour de chaque côté : le tri exact se fait en dates locales, juste dessous.
            expires_at__gte=maintenant - timedelta(days=1),
            expires_at__lte=maintenant + timedelta(days=JOURS_AVANT_MAX + 1),
            user__email_verified=True, user__email__isnull=False, user__is_active=True,
            cursus__country__actif=True,
        )
        .exclude(user__email="")
        .select_related("user__cursus_prepare", "profil", "cursus__country", "cursus__series")
    )
    dues = []
    for abonnement in candidats:
        jours = (timezone.localtime(abonnement.expires_at).date() - aujourdhui).days
        for type_, debut, fin in FENETRES:
            if debut <= jours <= fin:
                dues.append((abonnement, type_, reference_de(abonnement)))
    if not dues:
        return []

    deja = set(
        RelanceEnvoyee.objects.filter(
            type__in=[t for t, _d, _f in FENETRES], user_id__in={a.user_id for a, _t, _r in dues},
        ).values_list("user_id", "type", "reference"),
    )
    paiements_en_cours = set(
        ManualPayment.objects.filter(
            status=ManualPaymentStatus.PENDING, user_id__in={a.user_id for a, _t, _r in dues},
        ).values_list("user_id", "profil_id", "plan__cursus_id"),
    )
    examens_passes = {}
    retenues = []
    for abonnement, type_, reference in dues:
        if (abonnement.user_id, type_, reference) in deja:
            continue
        if (abonnement.user_id, abonnement.profil_id, abonnement.cursus_id) in paiements_en_cours:
            continue
        if abonnement.cursus_id not in examens_passes:
            examens_passes[abonnement.cursus_id] = _examen_passe(abonnement.cursus)
        if examens_passes[abonnement.cursus_id]:
            continue
        retenues.append((abonnement, type_, reference))
    return retenues


def envoyer_relances_fin_abonnement(maintenant=None, *, dry_run=False):
    envoyes = 0
    for abonnement, type_, reference in relances_fin_abonnement_dues(maintenant):
        if dry_run:
            envoyes += 1
            continue
        user = abonnement.user
        try:
            sujet, corps = composer_relance_fin_abonnement(abonnement, type_)
            if not _tracer(user, type_, reference):
                continue
            try:
                _envoyer_email(user, sujet, corps)
            except Exception:
                # Un envoi raté ne doit pas rester marqué « fait » : le tour suivant le retentera, dans sa fenêtre.
                RelanceEnvoyee.objects.filter(user=user, type=type_, reference=reference).delete()
                raise
            envoyes += 1
        except Exception:
            logger.exception("Relance de fin d'abonnement non envoyée au compte %s", user.pk)
    return envoyes
