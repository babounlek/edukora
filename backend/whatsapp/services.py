"""
Consentement (opt-in/opt-out) et envoi des rappels de révision WhatsApp - réutilise
quiz.services.revisions_dues (déjà la source de vérité de "quoi réviser aujourd'hui",
déjà exploitée côté web par quiz.views.list_revisions_dues) plutôt que d'inventer un
second calcul de retard de révision.
"""

from django.utils import timezone

from quiz.services import revisions_dues

from .backends import get_whatsapp_backend
from .models import OptIn

# Nom du template WhatsApp à soumettre à l'approbation Meta (voir le brouillon de
# corps de message discuté avec l'utilisateur) - une constante ici, jamais répétée en
# dur dans backends.py, pour qu'un renommage du template approuvé ne se corrige qu'à
# un seul endroit.
REMINDER_TEMPLATE_NAME = "rappel_revision_quotidien"

# Nombre de thèmes cités nommément dans le message - un template WhatsApp approuvé a
# une longueur de variable limitée, et énumérer 15 notions n'aiderait de toute façon
# pas plus qu'un chiffre + les premières (voir _format_themes).
THEMES_CITES_MAX = 3


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
