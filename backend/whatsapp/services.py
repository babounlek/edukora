"""
Consentement (opt-in/opt-out) et envoi des rappels de révision WhatsApp - réutilise
quiz.services.revisions_dues (déjà la source de vérité de "quoi réviser aujourd'hui",
déjà exploitée côté web par quiz.views.list_revisions_dues) plutôt que d'inventer un
second calcul de retard de révision.

Contient aussi le traitement des messages ENTRANTS (traiter_payload_entrant), appelé
par whatsapp.webhook une fois la notification authentifiée : un utilisateur doit
pouvoir se désabonner en répondant "STOP" dans WhatsApp, sans passer par la page
/compte - exigence de la politique WhatsApp Business, pas un confort ajouté ici.
"""

import logging
import re
import unicodedata

from django.core.exceptions import ValidationError
from django.utils import timezone

from quiz.services import revisions_dues
from users.models import User
from users.phone import to_e164, to_local

from .backends import get_whatsapp_backend
from .models import OptIn

logger = logging.getLogger("whatsapp")

# Nom du template WhatsApp à soumettre à l'approbation Meta (voir le brouillon de
# corps de message discuté avec l'utilisateur) - une constante ici, jamais répétée en
# dur dans backends.py, pour qu'un renommage du template approuvé ne se corrige qu'à
# un seul endroit.
REMINDER_TEMPLATE_NAME = "rappel_revision_quotidien"

# Nombre de thèmes cités nommément dans le message - un template WhatsApp approuvé a
# une longueur de variable limitée, et énumérer 15 notions n'aiderait de toute façon
# pas plus qu'un chiffre + les premières (voir _format_themes).
THEMES_CITES_MAX = 3

# Mots-clés d'arrêt reconnus dans un message entrant (voir est_demande_arret, qui les
# compare après suppression des accents et de la ponctuation - inutile de lister ici
# les variantes accentuées « arrêt »/« désabonner »). Français ET anglais : le clavier
# d'un élève propose souvent "stop" en premier, et un désabonnement raté est une
# violation de la politique WhatsApp Business, pas un simple défaut d'ergonomie.
MOTS_CLES_ARRET = {"stop", "arret", "arreter", "desabonner", "desabonnement", "unsubscribe"}


def is_opted_in(user):
    return OptIn.objects.filter(user=user, opted_out_at__isnull=True).exists()


def opt_in(user):
    """Idempotent : un utilisateur déjà opt-in n'obtient pas une seconde ligne active
    (voir OptIn, docstring de modèle - seul un nouvel aller-retour opt-out/opt-in en
    crée une)."""
    if is_opted_in(user):
        return
    OptIn.objects.create(user=user)


def opt_out(user):
    OptIn.objects.filter(user=user, opted_out_at__isnull=True).update(opted_out_at=timezone.now())


def _format_themes(schedules):
    noms = [s.theme.name for s in schedules[:THEMES_CITES_MAX]]
    reste = len(schedules) - len(noms)
    texte = ", ".join(noms)
    if reste > 0:
        texte += f" (+{reste} autre{'s' if reste > 1 else ''})"
    return texte


def utilisateurs_a_relancer():
    """Génère (user, schedules) pour chaque utilisateur actuellement opt-in ayant au
    moins une révision due aujourd'hui (voir quiz.services.revisions_dues) - jamais
    un utilisateur opt-in sans rien à réviser, un rappel vide n'aurait aucun sens."""
    for optin in OptIn.objects.filter(opted_out_at__isnull=True).select_related("user"):
        schedules = list(revisions_dues(optin.user))
        if schedules:
            yield optin.user, schedules


def envoyer_rappels_du_jour():
    """
    Point d'entrée de la commande de gestion send_whatsapp_reminders - un rappel par
    utilisateur opt-in ayant au moins une révision due. Retourne le nombre de rappels
    envoyés. Censée tourner une fois par jour via une tâche planifiée externe (voir la
    docstring de la commande) - aucune déduplication supplémentaire nécessaire ici,
    l'appelant est responsable de la cadence.
    """
    backend = get_whatsapp_backend()
    envoyes = 0
    for user, schedules in utilisateurs_a_relancer():
        backend.send_template(
            user.phone_number,
            REMINDER_TEMPLATE_NAME,
            [len(schedules), _format_themes(schedules)],
        )
        envoyes += 1
    return envoyes


def _normaliser(texte):
    """Minuscules, sans accents ni ponctuation : « ARRÊT ! » et « arret » doivent
    déclencher le même désabonnement."""
    decompose = unicodedata.normalize("NFKD", texte or "")
    sans_accent = "".join(c for c in decompose if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", sans_accent.lower()).strip()


def est_demande_arret(texte):
    """
    Seul le PREMIER mot est testé : « STOP rappels », « stop svp » ou « ARRÊT. » sont
    des demandes aussi explicites que « STOP » seul, et exiger une correspondance
    exacte laisserait un utilisateur inscrit malgré une demande claire - le risque à
    éviter en priorité de ce côté-ci (l'erreur inverse, désabonner un peu trop
    largement, se répare d'un clic dans /compte).
    """
    mots = _normaliser(texte).split()
    return bool(mots) and mots[0] in MOTS_CLES_ARRET


def utilisateur_par_numero(numero):
    """
    Retrouve l'utilisateur derrière un numéro reçu de Meta (chiffres seuls, indicatif
    compris - voir users.phone.to_msisdn pour la frontière symétrique en sortie).

    Interroge les DEUX formes qui coexistent réellement en base : l'E.164 canonique et
    le format local historique à 9 chiffres, dont la migration n'est pas terminée (voir
    users.phone, docstring de module). Ne chercher que l'E.164 ferait silencieusement
    échouer le désabonnement des comptes les plus anciens.
    """
    try:
        e164 = to_e164(numero)
    except ValidationError:
        return None
    if not e164:
        return None
    return User.objects.filter(phone_number__in=[e164, to_local(e164)]).first()


def traiter_payload_entrant(payload):
    """
    Applique les demandes d'arrêt contenues dans une notification webhook Meta DÉJÀ
    authentifiée (whatsapp.webhook.verifier_signature l'a fait ; on ne revérifie rien
    ici). Retourne le nombre de désabonnements effectués.

    Tout le reste du payload est ignoré volontairement : les accusés de réception
    (`statuses`) et les messages non textuels n'ont aucune action associée aujourd'hui.
    Même raisonnement pour la traversée défensive en .get() partout - une forme
    inattendue ne doit jamais lever, sinon Meta retente la même notification en boucle
    pendant des heures.
    """
    arrets = 0
    for entry in payload.get("entry") or []:
        for change in entry.get("changes") or []:
            for message in (change.get("value") or {}).get("messages") or []:
                if message.get("type") != "text":
                    continue
                if not est_demande_arret((message.get("text") or {}).get("body", "")):
                    continue
                numero = message.get("from") or ""
                user = utilisateur_par_numero(numero)
                if user is None:
                    # Numéro tronqué dans le journal : il n'est pas en base, donc pas
                    # couvert par le consentement du compte auquel il aurait appartenu.
                    logger.warning("Demande d'arrêt WhatsApp d'un numéro inconnu (…%s).", numero[-4:])
                    continue
                opt_out(user)
                arrets += 1
                logger.info("Désabonnement WhatsApp de l'utilisateur #%s sur message entrant.", user.pk)
    return arrets
