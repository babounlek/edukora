"""
Relances d'absence (audit 14, F2) : deux messages, puis le silence.

- le premier quand l'élève a manqué deux jours pleins : il rappelle que la reprise est courte, sans reproche ;
- le second, et dernier, quand il a manqué une semaine : il dit franchement que nous n'écrirons plus.

Entre les deux et après le second, rien ne part - ni ces messages ni le rappel quotidien (voir relances.activite) - tant que
l'élève n'a pas retravaillé. À son retour, tout reprend : la trace d'envoi porte la date de son dernier jour travaillé, une
nouvelle absence est donc un nouvel épisode.

Mêmes conditions que le rappel quotidien (voir relances.services.destinataires_rappel_seance) : rappels demandés, adresse
confirmée, examen déclaré, abonnement actif. Un élève qui a coupé les rappels ne reçoit pas non plus ceux-ci. Par e-mail
seulement pour l'instant.
"""
import logging

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

from quiz import textes
from quiz.services import revisions_dues
from users.models import User

from .activite import jours_sans_travail
from .models import RelanceEnvoyee, TypeRelance
from .services import _envoyer_email, _formule_examen, _salutation, _tracer, langue_du_compte, lien_desabonnement

logger = logging.getLogger(__name__)

# Jours écoulés depuis le dernier jour travaillé (voir relances.activite) : 3 = deux jours pleins manqués, 8 = sept.
# Chaque message a deux jours pour partir : si l'ordonnanceur a manqué le premier soir, il part le lendemain, pas plus tard
# (un « ça fait deux jours » reçu au sixième jour serait faux).
FENETRES = (
    (TypeRelance.ABSENCE_1, 3, 4),
    (TypeRelance.ABSENCE_2, 8, 9),
)

_TEXTES = {
    TypeRelance.ABSENCE_1: {
        textes.FR: {
            "lang": "fr",
            "sujet": "On reprend ? 25 minutes suffisent",
            "slogan": "Réussis ton examen",
            "titre": "On reprend où tu en étais",
            "intro": "Deux jours sans séance : rien de grave. Une séance d'environ 25 minutes suffit pour reprendre le fil, "
                     "et ta progression est gardée.",
            "intro_avant": "Deux jours sans séance : rien de grave. Une séance d'environ",
            "intro_duree": "25 minutes",
            "intro_apres": " suffit pour reprendre le fil, et ta progression est gardée.",
            "apercu": "Deux jours sans séance : rien de grave, on reprend où tu en étais.",
            "bouton": "Reprendre ma préparation",
            "secours": "Le bouton ne s'affiche pas ? Copie ce lien dans ton navigateur :",
            "raison": "Tu reçois ce message parce que tu as activé les rappels. Nous ne t'écrirons pas tous les jours "
                      "pendant ton absence.",
            "arret": "Les arrêter en un clic",
            "question": "Une question ? Réponds simplement à ce message ou écris à",
        },
        textes.EN: {
            "lang": "en",
            "sujet": "Shall we pick it up again? 25 minutes is enough",
            "slogan": "Pass your exam",
            "titre": "Pick up where you left off",
            "intro": "Two days without a session: no big deal. One session of about 25 minutes is enough to get back on "
                     "track, and your progress is saved.",
            "intro_avant": "Two days without a session: no big deal. One session of about",
            "intro_duree": "25 minutes",
            "intro_apres": " is enough to get back on track, and your progress is saved.",
            "apercu": "Two days without a session: no big deal, pick up where you left off.",
            "bouton": "Resume my preparation",
            "secours": "Can't see the button? Copy this link into your browser:",
            "raison": "You receive this message because you turned on reminders. We won't write to you every day while "
                      "you are away.",
            "arret": "Stop them in one click",
            "question": "A question? Just reply to this message or write to",
        },
    },
    TypeRelance.ABSENCE_2: {
        textes.FR: {
            "lang": "fr",
            "sujet": "Notre dernier rappel : ta préparation t'attend",
            "slogan": "Réussis ton examen",
            "titre": "Ta préparation t'attend",
            "intro": "Une semaine sans séance. C'est notre dernier message : nous ne t'écrirons plus tant que tu n'es pas "
                     "revenu. Rien n'est perdu, tu reprends où tu en étais, en environ 25 minutes.",
            "intro_avant": "Une semaine sans séance. C'est notre dernier message : nous ne t'écrirons plus tant que tu "
                           "n'es pas revenu. Rien n'est perdu, tu reprends où tu en étais, en environ",
            "intro_duree": "25 minutes",
            "intro_apres": ".",
            "apercu": "Notre dernier message : rien n'est perdu, tu reprends où tu en étais.",
            "bouton": "Reprendre ma préparation",
            "secours": "Le bouton ne s'affiche pas ? Copie ce lien dans ton navigateur :",
            "raison": "Tu reçois ce message parce que tu as activé les rappels. C'est le dernier avant ton retour.",
            "arret": "Les arrêter en un clic",
            "question": "Une question ? Réponds simplement à ce message ou écris à",
        },
        textes.EN: {
            "lang": "en",
            "sujet": "Our last reminder: your preparation is waiting",
            "slogan": "Pass your exam",
            "titre": "Your preparation is waiting",
            "intro": "A week without a session. This is our last message: we won't write again until you come back. "
                     "Nothing is lost, you pick up where you left off, in about 25 minutes.",
            "intro_avant": "A week without a session. This is our last message: we won't write again until you come "
                           "back. Nothing is lost, you pick up where you left off, in about",
            "intro_duree": "25 minutes",
            "intro_apres": ".",
            "apercu": "Our last message: nothing is lost, you pick up where you left off.",
            "bouton": "Resume my preparation",
            "secours": "Can't see the button? Copy this link into your browser:",
            "raison": "You receive this message because you turned on reminders. It is the last one until you come back.",
            "arret": "Stop them in one click",
            "question": "A question? Just reply to this message or write to",
        },
    },
}


def composer_relance_absence(user, type_):
    """(sujet, corps, html) d'une relance d'absence. Comme le rappel quotidien : rien n'est créé au nom de l'élève, le texte
    brut est le message de référence et le HTML (même gabarit) en reprend les mêmes faits."""
    profil = user.profils.first()
    cursus = user.cursus_prepare
    langue = langue_du_compte(user)
    anglais = langue == textes.EN
    t = _TEXTES[type_][langue]
    faits = []

    formule = _formule_examen(cursus, langue)
    if formule:
        faits.append(formule)
    dues = revisions_dues(profil, cursus).count() if profil is not None else 0
    if dues:
        faits.append(
            f"{dues} topic{'s' if dues > 1 else ''} waiting to be reviewed." if anglais
            else f"{dues} thème{'s' if dues > 1 else ''} à revoir t'attend{'ent' if dues > 1 else ''}."
        )

    pays = cursus.country.code.lower()
    lien = f"{settings.FRONTEND_URL}/en/{pays}" if anglais else f"{settings.FRONTEND_URL}/{pays}"
    lien_arret = lien_desabonnement(user)
    salutation = _salutation(user, langue)
    texte = [salutation, "", t["intro"], *faits, "", f"{t['bouton']} : {lien}", "", t["raison"], f"{t['arret']} : {lien_arret}"]
    html = render_to_string(
        "relances/emails/rappel_seance.html",
        {
            "site_name": settings.SITE_NAME, "salutation": salutation, "faits": faits, "lien": lien,
            "lien_desabonnement": lien_arret, "apercu": t["apercu"], "t": t,
            "site_url": settings.FRONTEND_URL, "support_email": settings.SUPPORT_EMAIL,
        },
    )
    return t["sujet"], "\n".join(texte), html


def relances_absence_dues(maintenant=None):
    """
    [(élève, type, référence)] : les relances d'absence à envoyer maintenant. La référence est la date du dernier jour
    travaillé : un message par étape et par absence, jamais deux.
    """
    aujourdhui = timezone.localtime(maintenant).date() if maintenant else timezone.localdate()
    candidats = list(
        User.objects.filter(
            rappels_actifs=True, email_verified=True, email__isnull=False, cursus_prepare__isnull=False,
            cursus_prepare__country__actif=True, subscriptions__expires_at__gt=timezone.now(),
        )
        .select_related("cursus_prepare__country", "cursus_prepare__series")
        .distinct()
    )
    ecoules = jours_sans_travail([u.pk for u in candidats], aujourdhui)
    dues = []
    for user in candidats:
        jours, dernier = ecoules[user.pk]
        for type_, debut, fin in FENETRES:
            if debut <= jours <= fin:
                dues.append((user, type_, dernier.isoformat()))
    if not dues:
        return []
    deja = set(
        RelanceEnvoyee.objects.filter(
            type__in=[t for t, _d, _f in FENETRES], user_id__in=[u.pk for u, _t, _r in dues],
        ).values_list("user_id", "type", "reference"),
    )
    return [(user, type_, reference) for user, type_, reference in dues if (user.pk, type_, reference) not in deja]


def envoyer_relances_absence(maintenant=None, *, dry_run=False):
    envoyes = 0
    for user, type_, reference in relances_absence_dues(maintenant):
        if dry_run:
            envoyes += 1
            continue
        try:
            sujet, corps, html = composer_relance_absence(user, type_)
            if not _tracer(user, type_, reference):
                continue
            try:
                _envoyer_email(user, sujet, corps, html)
            except Exception:
                # Un envoi raté ne doit pas rester marqué « fait » : le tour suivant le retentera, dans sa fenêtre.
                RelanceEnvoyee.objects.filter(user=user, type=type_, reference=reference).delete()
                raise
            envoyes += 1
        except Exception:
            logger.exception("Relance d'absence non envoyée à l'élève %s", user.pk)
    return envoyes
