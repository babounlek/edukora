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
from django.core.mail import EmailMultiAlternatives
from django.db import IntegrityError
from django.template.loader import render_to_string
from django.utils import timezone

from catalog.models import ExamSession
from payments.models import ManualPayment, ManualPaymentStatus, StatutTransaction, Transaction
from quiz import textes
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


def langue_du_compte(user):
    """'en' dès que le compte a choisi l'anglais ou prépare un examen anglophone (GCE), 'fr' sinon -
    même règle que le rappel push (voir relances.push.composer_push). Un élève du GCE et son parent
    recevaient leurs e-mails en français."""
    if getattr(user, "langue", textes.FR) == textes.EN:
        return textes.EN
    return textes.langue_de(getattr(user, "cursus_prepare", None))


def _salutation(user, langue=textes.FR):
    prenom = _prenom(user)
    if langue == textes.EN:
        return f"Hello {prenom}," if prenom else "Hello,"
    return f"Bonjour {prenom}," if prenom else "Bonjour,"


def _envoyer_email(user, sujet, corps, html=None):
    # Texte brut toujours fourni, HTML en alternative (voir users.email_service). Reply-To sur la boîte surveillée :
    # « réponds simplement à ce message » ne doit pas tomber dans une adresse d'expédition jamais relevée.
    message = EmailMultiAlternatives(sujet, corps, None, [user.email], reply_to=[settings.SUPPORT_EMAIL])
    if html:
        message.attach_alternative(html, "text/html")
    message.send(fail_silently=False)


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


def _formule_examen(cursus, langue=textes.FR):
    compte = ExamSession.compte_a_rebours_pour(cursus)
    if not compte or compte["jours_restants"] < 0:
        return ""
    jours = compte["jours_restants"]
    libelle = str(cursus)
    if langue == textes.EN:
        if compte.get("estimee"):
            return f"Your exam ({libelle}) is coming up: about {round(jours / 30)} months left."
        return f"{jours} day{'s' if jours != 1 else ''} until your exam ({libelle})."
    if compte.get("estimee"):
        return f"Ton examen ({libelle}) approche : il reste environ {round(jours / 30)} mois."
    return f"Il reste {jours} jour{'s' if jours > 1 else ''} avant ton examen ({libelle})."


# Les textes fixes du rappel quotidien, dans les deux langues : le texte brut et le gabarit HTML
# (relances/emails/rappel_seance.html) lisent les mêmes.
_TEXTES_RAPPEL = {
    textes.FR: {
        "lang": "fr",
        "sujet": "Ta séance du jour est prête",
        "slogan": "Réussis ton examen",
        "titre": "Ta séance du jour t'attend",
        "intro": "Ta séance du jour t'attend : environ 25 minutes, choisie pour toi.",
        "intro_avant": "Environ",
        "intro_duree": "25 minutes",
        "intro_apres": ", choisies pour toi parmi ce qui te fera le plus progresser aujourd'hui.",
        "apercu": "Environ 25 minutes, choisies pour toi.",
        "bouton": "Ouvrir ma séance",
        "secours": "Le bouton ne s'affiche pas ? Copie ce lien dans ton navigateur :",
        "raison": "Tu reçois ce message parce que tu as activé les rappels quotidiens.",
        "arret": "Les arrêter en un clic",
        "question": "Une question ? Réponds simplement à ce message ou écris à",
    },
    textes.EN: {
        "lang": "en",
        "sujet": "Your daily session is ready",
        "slogan": "Pass your exam",
        "titre": "Your daily session is waiting",
        "intro": "Your daily session is waiting: about 25 minutes, chosen for you.",
        "intro_avant": "About",
        "intro_duree": "25 minutes",
        "intro_apres": ", chosen for you from what will move you forward the most today.",
        "apercu": "About 25 minutes, chosen for you.",
        "bouton": "Open my session",
        "secours": "Can't see the button? Copy this link into your browser:",
        "raison": "You receive this message because you turned on daily reminders.",
        "arret": "Stop them in one click",
        "question": "A question? Just reply to this message or write to",
    },
}


def composer_rappel_seance(user):
    """(sujet, corps, html) du rappel quotidien - sans jamais créer la séance elle-même :
    ouvrir l'application la crée, l'envoi d'un e-mail ne doit rien inscrire au nom de
    l'élève (ni fausser ce que mesure l'entonnoir d'acquisition). Le texte brut reste le
    message de référence ; le HTML en reprend exactement les mêmes faits."""
    # Même repli que users.profils.profil_actif : chaque compte n'a aujourd'hui qu'un
    # seul profil, la vraie bascule (JWT claim) n'étant pas branchée sur ce canal
    # hors requête HTTP.
    profil = user.profils.first()
    cursus = user.cursus_prepare
    langue = langue_du_compte(user)
    anglais = langue == textes.EN
    t = _TEXTES_RAPPEL[langue]
    faits = []

    formule = _formule_examen(cursus, langue)
    if formule:
        faits.append(formule)

    serie = serie_de_jours(profil)
    if serie["jours"] >= 2:
        faits.append(
            f"Your streak is at {serie['jours']} days in a row." if anglais
            else f"Ta série est à {serie['jours']} jours de suite."
        )

    dues = revisions_dues(profil, cursus).count()
    if dues:
        faits.append(
            f"{dues} topic{'s' if dues > 1 else ''} to review today so {'they stay' if dues > 1 else 'it stays'} in memory."
            if anglais
            else f"{dues} thème{'s' if dues > 1 else ''} à revoir aujourd'hui pour qu'il{'s' if dues > 1 else ''} "
                 f"reste{'nt' if dues > 1 else ''} en mémoire."
        )

    pays = cursus.country.code.lower()
    lien = f"{settings.FRONTEND_URL}/en/{pays}" if anglais else f"{settings.FRONTEND_URL}/{pays}"
    lien_arret = lien_desabonnement(user)
    salutation = _salutation(user, langue)

    texte = [salutation, "", t["intro"], *faits]
    texte += ["", f"{t['bouton']} : {lien}", "", t["raison"], f"{t['arret']} : {lien_arret}"]
    html = render_to_string(
        "relances/emails/rappel_seance.html",
        {
            "site_name": settings.SITE_NAME, "salutation": salutation, "faits": faits, "lien": lien,
            "lien_desabonnement": lien_arret, "apercu": t["apercu"], "t": t,
            "site_url": settings.FRONTEND_URL, "support_email": settings.SUPPORT_EMAIL,
        },
    )
    return t["sujet"], "\n".join(texte), html


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
    destinataires = (
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
    # Un seul rappel par jour, tous canaux confondus, et la notification d'abord : elle part à l'heure où
    # l'élève travaille d'habitude (voir relances.push.heure_habituelle). L'e-mail de 17 h posait sa trace
    # avant elle, et un élève qui travaille à 20 h ne recevait jamais sa notification. Qui a un appareil
    # abonné est donc servi par la notification, pas par l'e-mail.
    from .push import push_configure

    if push_configure():
        destinataires = destinataires.exclude(abonnements_push__isnull=False)
    # Le rappel quotidien accompagne un élève qui travaille : deux jours pleins manqués et il se tait, les relances
    # d'absence prennent le relais (deux messages, puis le silence - voir relances.activite et relances.absence).
    from .activite import comptes_en_pause

    en_pause = comptes_en_pause(destinataires.values_list("pk", flat=True), aujourdhui)
    if en_pause:
        destinataires = destinataires.exclude(pk__in=en_pause)
    return destinataires


def envoyer_rappels_seance(maintenant=None, *, dry_run=False):
    aujourdhui = timezone.localtime(maintenant).date() if maintenant else timezone.localdate()
    envoyes = 0
    for user in destinataires_rappel_seance(maintenant):
        if dry_run:
            envoyes += 1
            continue
        try:
            sujet, corps, html = composer_rappel_seance(user)
            if not _tracer(user, TypeRelance.RAPPEL_SEANCE, aujourdhui.isoformat()):
                continue
            try:
                _envoyer_email(user, sujet, corps, html)
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
        reprise = ("tu peux réessayer, ou payer par transfert manuel (Orange Money ou MTN MoMo) sans rien perdre "
                   "de ta sélection." if settings.MANUAL_PAYMENT_ACTIVE else "tu peux réessayer.")
        lignes += [f"Rien n'a été débité pour un accès que tu n'as pas reçu : {reprise}"]
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
