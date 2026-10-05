"""Ordonnanceur des relances : fenêtre horaire du rappel, tour unique."""

from datetime import datetime
from io import StringIO
from zoneinfo import ZoneInfo

from django.core import mail
from django.core.management import call_command

from .management.commands.planifier_relances import passer_une_fois
from .tests import RelancesTestCase

DOUALA = ZoneInfo("Africa/Douala")


class PlanificateurTests(RelancesTestCase):
    def test_le_rappel_ne_part_que_dans_la_fenetre_de_fin_d_apres_midi(self):
        self.eleve()

        matin = datetime(2026, 9, 28, 9, 0, tzinfo=DOUALA)
        self.assertEqual(passer_une_fois(matin)["rappel"], 0)
        self.assertEqual(mail.outbox, [])

        soir = datetime(2026, 9, 28, 17, 30, tzinfo=DOUALA)
        self.assertEqual(passer_une_fois(soir)["rappel"], 1)
        self.assertEqual(len(mail.outbox), 1)

        # Le tour suivant, dans la même fenêtre, ne renvoie rien.
        self.assertEqual(passer_une_fois(datetime(2026, 9, 28, 18, 30, tzinfo=DOUALA))["rappel"], 0)

    def test_le_rappel_whatsapp_suit_la_meme_fenetre_et_part_une_fois_par_jour(self):
        from unittest import mock

        with mock.patch(
            "relances.management.commands.planifier_relances.envoyer_rappels_whatsapp", return_value=2,
        ) as whatsapp:
            self.assertEqual(passer_une_fois(datetime(2026, 9, 28, 9, 0, tzinfo=DOUALA))["whatsapp"], 0)
            whatsapp.assert_not_called()
            self.assertEqual(passer_une_fois(datetime(2026, 9, 28, 17, 30, tzinfo=DOUALA))["whatsapp"], 2)
            whatsapp.assert_called_once()
            self.assertEqual(passer_une_fois(datetime(2026, 9, 28, 21, 0, tzinfo=DOUALA))["whatsapp"], 0)
            whatsapp.assert_called_once()

    def test_pas_de_rappel_apres_la_fenetre(self):
        self.eleve()
        self.assertEqual(passer_une_fois(datetime(2026, 9, 28, 21, 0, tzinfo=DOUALA))["rappel"], 0)

    def test_la_commande_fait_un_tour_et_sort(self):
        sortie = StringIO()
        call_command("planifier_relances", "--une-fois", stdout=sortie)

    def test_un_tour_en_echec_n_arrete_pas_la_commande(self):
        from unittest import mock

        with mock.patch(
            "relances.management.commands.planifier_relances.passer_une_fois", side_effect=RuntimeError("panne"),
        ):
            call_command("planifier_relances", "--une-fois", stdout=StringIO())
