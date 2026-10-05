import logging
import time

from django.core.management.base import BaseCommand
from django.utils import timezone

from relances.bilan_parent import HEURE_DEBUT_BILAN, HEURE_FIN_BILAN, JOUR_ENVOI, envoyer_bilans_parent
from relances.push import envoyer_rappels_push
from relances.services import envoyer_relances_paiement, envoyer_rappels_seance
from whatsapp.services import envoyer_rappels_du_jour as envoyer_rappels_whatsapp

logger = logging.getLogger("relances")

# Fenêtre d'envoi du rappel quotidien, en heure LOCALE (settings.TIME_ZONE) : en fin de
# journée scolaire, quand une séance de 25 minutes a une chance d'être faite. Elle dure trois
# heures pour qu'un envoi raté à 17 h soit retenté à 18 h - le rappel ne part de toute façon
# qu'une fois par jour (voir relances.models.RelanceEnvoyee).
HEURE_DEBUT_RAPPEL = 17
HEURE_FIN_RAPPEL = 20


def passer_une_fois(maintenant=None):
    """Un tour : relance des paiements, rappel e-mail dans sa fenêtre horaire, et rappel push à
    l'heure habituelle de chaque élève (qui peut tomber hors de cette fenêtre : il choisit lui-même
    son heure en travaillant, voir relances.push.heure_habituelle)."""
    maintenant = maintenant or timezone.now()
    resultat = {"paiement": envoyer_relances_paiement(maintenant), "rappel": 0, "push": 0, "bilan": 0, "whatsapp": 0}
    # Le bilan du parent : le dimanche en fin d'après-midi, une fois par semaine (la trace par
    # semaine ISO empêche tout doublon si plusieurs tours tombent dans la fenêtre).
    local = timezone.localtime(maintenant)
    if local.weekday() == JOUR_ENVOI and HEURE_DEBUT_BILAN <= local.hour < HEURE_FIN_BILAN:
        resultat["bilan"] = envoyer_bilans_parent(maintenant)
    # Le push d'abord : un élève prévenu par notification ne reçoit pas en plus l'e-mail du même
    # jour (voir relances.push, une seule relance par jour tous canaux confondus).
    resultat["push"] = envoyer_rappels_push(maintenant)
    if HEURE_DEBUT_RAPPEL <= timezone.localtime(maintenant).hour < HEURE_FIN_RAPPEL:
        resultat["rappel"] = envoyer_rappels_seance(maintenant)
        # WhatsApp : canal à part (l'élève l'a demandé explicitement dans /compte), même
        # fenêtre que l'e-mail, une fois par jour (trace par canal dans RelanceEnvoyee).
        resultat["whatsapp"] = envoyer_rappels_whatsapp(maintenant)
    return resultat


class Command(BaseCommand):
    help = (
        "Ordonnanceur des relances e-mail : tourne en continu (service `relances` de "
        "docker-compose.yml) et exécute un tour par heure. Aucun cron externe à configurer."
    )

    def add_arguments(self, parser):
        parser.add_argument("--intervalle", type=int, default=3600, help="Secondes entre deux tours (défaut : 3600).")
        parser.add_argument("--une-fois", action="store_true", help="Un seul tour puis sortie (tests, essai manuel).")

    def handle(self, *args, **options):
        while True:
            try:
                resultat = passer_une_fois()
                if any(resultat.values()):
                    self.stdout.write(f"Relances envoyées : {resultat}")
            except Exception:
                # Un tour raté ne doit jamais arrêter l'ordonnanceur : le suivant réessaiera.
                logger.exception("Tour de relances en échec")
            if options["une_fois"]:
                return
            time.sleep(options["intervalle"])
