"""
Messages de relance - deux seulement, choisis parce qu'ils servent l'élève avant nous :

- le rappel quotidien de la séance du jour, pour qui l'a demandé (User.rappels_actifs) ;
- la relance d'un paiement qui n'a pas abouti, pour qui a essayé de payer et n'a rien
  reçu : c'est un suivi de SA démarche, pas de la publicité, limité à deux messages.

Aucun message n'est envoyé sans e-mail CONFIRMÉ (User.email_verified) : écrire à une
adresse jamais vérifiée revient à écrire à un inconnu. Chaque envoi est tracé
(RelanceEnvoyee) pour ne jamais partir deux fois.

Le canal e-mail est le seul branché aujourd'hui. WhatsApp existe (voir whatsapp.services)
mais reste bloqué tant que son modèle de message n'est pas approuvé par Meta : il se
brancherait ici, à côté de `_envoyer_email`, sans toucher aux règles de sélection.
"""

import logging
from datetime import timedelta

from django.conf import settings
from django.core import signing
from django.core.mail import send_mail
from django.db import IntegrityError
from django.utils import timezone

from catalog.models import ExamSession
from payments.models import ManualPayment, ManualPaymentStatus, StatutTransaction, Transaction
from quiz.models import SeanceJournaliere, StatutSeance
from quiz.serie import serie_de_jours
from quiz.services import revisions_dues
from subscriptions.models import Subscription
from users.models import User

from .models import CanalRelance, RelanceEnvoyee, TypeRelance

logger = logging.getLogger("relances")

SALT_DESABONNEMENT = "relances-desabonnement"
# Un paiement raté est relancé une première fois quand l'élève a eu le temps de réessayer
# seul, une dernière fois quelques jours après, puis plus jamais.
DELAI_PREMIERE_RELANCE = timedelta(hours=2)
DELAI_DERNIERE_RELANCE = timedelta(hours=72)
FENETRE_RELANCE_PAIEMENT = timedelta(days=7)
# Une transaction encore « en attente » depuis moins que ça est en cours de confirmation.
DELAI_CONFIRMATION = timedelta(hours=1)


# --------------------------------------------------------------------------- désabonnement


def jeton_desabonnement(user):
    return signing.dumps({"u": user.pk}, salt=SALT_DESABONNEMENT)


def utilisateur_du_jeton(jeton):
    """L'élève désigné par un jeton de désabonnement, ou None si le jeton est altéré.
    Sans expiration : un lien de désabonnement doit marcher pour toujours."""
    try:
        return User.objects.filter(pk=signing.loads(jeton, salt=SALT_DESABONNEMENT)["u"]).first()
    except (signing.BadSignature, KeyError):
        return None


def lien_desabonnement(user):
    return f"{settings.FRONTEND_URL}/relances/desabonner/{jeton_desabonnement(user)}/"


# --------------------------------------------------------------------------- envoi


def _prenom(user):
    nom = (user.full_name or user.pseudo or "").strip()
    return nom.split()[0] if nom else ""


def _salutation(user):
    prenom = _prenom(user)
    return f"Bonjour {prenom}," if prenom else "Bonjour,"


def _envoyer_email(user, sujet, corps):
    send_mail(sujet, corps, None, [user.email], fail_silently=False)


def _tracer(user, type_, reference):
    """Enregistre l'envoi ; False si ce message était déjà parti (contrainte d'unicité)."""
    try:
        RelanceEnvoyee.objects.create(user=user, type=type_, reference=reference, canal=CanalRelance.EMAIL)
    except IntegrityError:
        return False
    return True


def _abonnement_actif(user):
    return Subscription.objects.filter(user=user, expires_at__gt=timezone.now()).exists()


# --------------------------------------------------------------------------- rappel de séance


def _formule_examen(cursus):
    compte = ExamSession.compte_a_rebours_pour(cursus)
    if not compte or compte["jours_restants"] < 0:
        return ""
    jours = compte["jours_restants"]
    libelle = str(cursus)
    if compte.get("estimee"):
        return f"Ton examen ({libelle}) approche : il reste environ {round(jours / 30)} mois."
    return f"Il reste {jours} jour{'s' if jours > 1 else ''} avant ton examen ({libelle})."


def composer_rappel_seance(user):
    """(sujet, corps) du rappel quotidien - sans jamais créer la séance elle-même :
    ouvrir l'application la crée, l'envoi d'un e-mail ne doit rien inscrire au nom de
    l'élève (ni fausser ce que mesure l'entonnoir d'acquisition)."""
    # Même repli que users.profils.profil_actif : chaque compte n'a aujourd'hui qu'un
    # seul profil, la vraie bascule (JWT claim) n'étant pas branchée sur ce canal
    # hors requête HTTP.
    profil = user.profils.first()
    cursus = user.cursus_prepare
    lignes = [_salutation(user), "", "Ta séance du jour t'attend : environ 25 minutes, choisie pour toi."]

    formule = _formule_examen(cursus)
    if formule:
        lignes.append(formule)

    serie = serie_de_jours(profil)
    if serie["jours"] >= 2:
        lignes.append(f"Ta série est à {serie['jours']} jours de suite.")

    dues = revisions_dues(profil, cursus).count()
    if dues:
        lignes.append(f"{dues} thème{'s' if dues > 1 else ''} à revoir aujourd'hui pour qu'il{'s' if dues > 1 else ''} restent en mémoire.")

    pays = cursus.country.code.lower()
    lignes += [
        "",
        f"Ouvrir ma séance : {settings.FRONTEND_URL}/{pays}",
        "",
        "Tu reçois ce message parce que tu as activé les rappels quotidiens.",
        f"Les arrêter en un clic : {lien_desabonnement(user)}",
    ]
    return "Ta séance du jour est prête", "\n".join(lignes)


def destinataires_rappel_seance(maintenant=None):
    """Élèves à qui envoyer le rappel aujourd'hui : rappels demandés, e-mail confirmé,
    abonnement actif (la séance est verrouillée sans), examen déclaré, séance pas encore
    terminée aujourd'hui et rappel pas déjà envoyé."""
    aujourdhui = timezone.localtime(maintenant).date() if maintenant else timezone.localdate()
    deja_fait = SeanceJournaliere.objects.filter(
        date=aujourdhui, statut=StatutSeance.TERMINEE,
    ).values("profil__compte_id")
    deja_relance = RelanceEnvoyee.objects.filter(
        type=TypeRelance.RAPPEL_SEANCE, reference=aujourdhui.isoformat(),
    ).values("user_id")
    return (
        User.objects.filter(
            rappels_actifs=True, email_verified=True, email__isnull=False, cursus_prepare__isnull=False,
            cursus_prepare__country__actif=True,
        )
        .exclude(pk__in=deja_fait)
        .exclude(pk__in=deja_relance)
        .filter(subscriptions__expires_at__gt=timezone.now())
        .select_related("cursus_prepare__country", "cursus_prepare__series")
        .distinct()
    )


def envoyer_rappels_seance(maintenant=None, *, dry_run=False):
    aujourdhui = timezone.localtime(maintenant).date() if maintenant else timezone.localdate()
    envoyes = 0
    for user in destinataires_rappel_seance(maintenant):
        if dry_run:
            envoyes += 1
            continue
        try:
            sujet, corps = composer_rappel_seance(user)
            if not _tracer(user, TypeRelance.RAPPEL_SEANCE, aujourdhui.isoformat()):
                continue
            try:
                _envoyer_email(user, sujet, corps)
            except Exception:
                # Un envoi raté ne doit pas être définitivement marqué « fait » : on retire la
                # trace pour qu'une nouvelle exécution le retente.
                RelanceEnvoyee.objects.filter(
                    user=user, type=TypeRelance.RAPPEL_SEANCE, reference=aujourdhui.isoformat(),
                ).delete()
                raise
            envoyes += 1
        except Exception:
            logger.exception("Rappel de séance non envoyé à l'élève %s", user.pk)
    return envoyes


# --------------------------------------------------------------------------- paiement non abouti


def _a_deja_paye(user):
    return (
        Transaction.objects.filter(user=user, status=StatutTransaction.SUCCESSFUL).exists()
        or ManualPayment.objects.filter(
            user=user, status__in=[ManualPaymentStatus.APPROVED, ManualPaymentStatus.PENDING],
        ).exists()
        or _abonnement_actif(user)
    )


def paiement_a_reprendre(user, maintenant=None):
    """La dernière tentative de paiement de l'élève si elle n'a pas abouti, il n'a rien payé
    d'autre et elle est assez récente pour valoir un rappel - sinon None. Source unique des
    relances par e-mail ET de la bannière « reprendre mon paiement » de l'application."""
    maintenant = maintenant or timezone.now()
    derniere = (
        Transaction.objects.filter(user=user, created_at__gte=maintenant - FENETRE_RELANCE_PAIEMENT)
        .select_related("plan__cursus").order_by("-created_at").first()
    )
    if derniere is None or derniere.status == StatutTransaction.SUCCESSFUL:
        return None
    if derniere.status == StatutTransaction.PENDING and maintenant - derniere.created_at < DELAI_CONFIRMATION:
        return None
    if _a_deja_paye(user):
        return None
    return derniere


def composer_relance_paiement(user, transaction, etape):
    """(sujet, corps) : `etape` vaut 1 (premier message) ou 2 (dernier)."""
    verbe = "n'a pas abouti" if transaction.status == StatutTransaction.FAILED else "n'a pas été confirmé"
    lien = f"{settings.FRONTEND_URL}/abonnement?cursus={transaction.plan.cursus_id}"
    lignes = [_salutation(user), "", f"Ton paiement de {transaction.amount} FCFA {verbe}."]
    if etape == 1:
        lignes += [
            "Rien n'a été débité pour un accès que tu n'as pas reçu : tu peux réessayer, ou payer par transfert "
            "manuel (Orange Money ou MTN MoMo) sans rien perdre de ta sélection.",
        ]
    else:
        lignes += [
            "C'est notre dernier message à ce sujet. Ton abonnement court jusqu'à ton examen : plus tôt tu "
            "l'actives, plus tu as de semaines de révision.",
        ]
    lignes += ["", f"Reprendre mon paiement : {lien}", "", "Une question ? Réponds simplement à ce message."]
    sujet = "Ton paiement n'a pas abouti" if etape == 1 else "Ton accès t'attend toujours"
    return sujet, "\n".join(lignes)


def _etape_due(user, transaction, maintenant):
    age = maintenant - transaction.created_at
    reference = str(transaction.pk)
    deja = set(
        RelanceEnvoyee.objects.filter(user=user, reference=reference).values_list("type", flat=True),
    )
    if TypeRelance.PAIEMENT_ABANDONNE_1 not in deja:
        return (1, TypeRelance.PAIEMENT_ABANDONNE_1) if age >= DELAI_PREMIERE_RELANCE else None
    if TypeRelance.PAIEMENT_ABANDONNE_2 not in deja and age >= DELAI_DERNIERE_RELANCE:
        return 2, TypeRelance.PAIEMENT_ABANDONNE_2
    return None


def envoyer_relances_paiement(maintenant=None, *, dry_run=False):
    maintenant = maintenant or timezone.now()
    envoyes = 0
    candidats = User.objects.filter(
        email_verified=True, email__isnull=False,
        transactions__created_at__gte=maintenant - FENETRE_RELANCE_PAIEMENT,
    ).distinct()
    for user in candidats:
        transaction = paiement_a_reprendre(user, maintenant)
        if transaction is None:
            continue
        etape = _etape_due(user, transaction, maintenant)
        if etape is None:
            continue
        numero, type_ = etape
        if dry_run:
            envoyes += 1
            continue
        try:
            if not _tracer(user, type_, str(transaction.pk)):
                continue
            try:
                sujet, corps = composer_relance_paiement(user, transaction, numero)
                _envoyer_email(user, sujet, corps)
            except Exception:
                RelanceEnvoyee.objects.filter(user=user, type=type_, reference=str(transaction.pk)).delete()
                raise
            envoyes += 1
        except Exception:
            logger.exception("Relance de paiement non envoyée à l'élève %s", user.pk)
    return envoyes
