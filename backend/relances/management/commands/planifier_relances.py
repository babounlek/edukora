import logging
import time

from django.core.management.base import BaseCommand
from django.utils import timezone

from relances.services import envoyer_relances_paiement, envoyer_rappels_seance

logger = logging.getLogger("relances")

# Fenêtre d'envoi du rappel quotidien, en heure LOCALE (settings.TIME_ZONE) : en fin de
# journée scolaire, quand une séance de 25 minutes a une chance d'être faite. Elle dure trois
# heures pour qu'un envoi raté à 17 h soit retenté à 18 h - le rappel ne part de toute façon
# qu'une fois par jour (voir relances.models.RelanceEnvoyee).
HEURE_DEBUT_RAPPEL = 17
HEURE_FIN_RAPPEL = 20


def passer_une_fois(maintenant=None):
    """Un tour : relance des paiements, et rappel de séance dans sa fenêtre horaire."""
    maintenant = maintenant or timezone.now()
    resultat = {"paiement": envoyer_relances_paiement(maintenant), "rappel": 0}
    if HEURE_DEBUT_RAPPEL <= timezone.localtime(maintenant).hour < HEURE_FIN_RAPPEL:
        resultat["rappel"] = envoyer_rappels_seance(maintenant)
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
                if resultat["paiement"] or resultat["rappel"]:
                    self.stdout.write(f"Relances envoyées : {resultat}")
            except Exception:
                # Un tour raté ne doit jamais arrêter l'ordonnanceur : le suivant réessaiera.
                logger.exception("Tour de relances en échec")
            if options["une_fois"]:
                return
            time.sleep(options["intervalle"])
