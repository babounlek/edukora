"""
Audit du 2026-11-16 (section 4.2) : un seul rappel par jour, la notification d'abord ; les e-mails dans la
langue du compte ; les purges quotidiennes et le rattrapage des paiements menés par l'ordonnanceur.
"""

from datetime import datetime, timedelta
from unittest import mock
from zoneinfo import ZoneInfo

from django.core import mail
from django.test import override_settings

from catalog.models import Cursus, Examen
from subscriptions.models import Subscription
from whatsapp import services as whatsapp
from whatsapp.models import OptIn

from . import bilan_parent, services
from .management.commands import planifier_relances
from .models import AbonnementPush, CanalRelance, RelanceEnvoyee, TypeRelance
from .tests import RelancesTestCase

DOUALA = ZoneInfo("Africa/Douala")
CLES_VAPID = {"VAPID_PUBLIC_KEY": "cle-publique", "VAPID_PRIVATE_KEY": "cle-privee", "VAPID_CLAIM_EMAIL": "contact@example.com"}


class UnSeulRappelParJourTests(RelancesTestCase):
    def _appareil(self, user):
        return AbonnementPush.objects.create(user=user, endpoint=f"https://push.example.com/{user.pk}", p256dh="p", auth="a")

    @override_settings(**CLES_VAPID)
    def test_qui_a_un_appareil_abonne_n_est_pas_servi_par_l_e_mail(self):
        # L'e-mail de 17 h posait sa trace avant la notification de 20 h, qui ne partait donc jamais.
        avec_appareil, sans_appareil = self.eleve(), self.eleve()
        self._appareil(avec_appareil)

        self.assertEqual(services.envoyer_rappels_seance(), 1)

        self.assertEqual([m.to for m in mail.outbox], [[sans_appareil.email]])
        self.assertFalse(RelanceEnvoyee.objects.filter(user=avec_appareil).exists())

    def test_sans_cles_de_notification_l_e_mail_part_pour_tous(self):
        user = self.eleve()
        self._appareil(user)

        self.assertEqual(services.envoyer_rappels_seance(), 1)


class LangueDuCompteTests(RelancesTestCase):
    def _eleve_gce(self):
        user = self.eleve()
        gce = Cursus.objects.get(examen=Examen.GCE_OL, series__isnull=True)
        user.cursus_prepare = gce
        user.save(update_fields=["cursus_prepare"])
        Subscription.objects.create(
            user=user, profil=user.profils.first(), cursus=gce, expires_at=self.maintenant + timedelta(days=30),
        )
        return user

    def test_le_rappel_d_un_eleve_du_gce_est_en_anglais(self):
        user = self._eleve_gce()

        sujet, corps, html = services.composer_rappel_seance(user)

        self.assertEqual(sujet, "Your daily session is ready")
        self.assertIn("Hello Awa,", corps)
        self.assertIn("Open my session", corps)
        self.assertIn("/en/", corps)
        self.assertNotIn("séance", corps)
        self.assertIn('lang="en"', html)
        self.assertIn("Stop them in one click", html)
        self.assertNotIn("Réussis ton examen", html)

    def test_le_rappel_francophone_ne_change_pas(self):
        sujet, corps, html = services.composer_rappel_seance(self.eleve())

        self.assertEqual(sujet, "Ta séance du jour est prête")
        self.assertIn("Bonjour Awa,", corps)
        self.assertIn("Ouvrir ma séance", html)
        self.assertIn('lang="fr"', html)

    def test_le_bilan_du_parent_suit_la_langue_du_compte(self):
        user = self._eleve_gce()

        sujet, corps, _html = bilan_parent.composer_bilan_parent(user)

        self.assertEqual(sujet, "Awa's week")
        self.assertIn("Here is the week that just ended:", corps)
        self.assertIn("Stop it in one click", corps)

    def test_un_compte_passe_en_anglais_recoit_l_anglais(self):
        user = self.eleve()
        user.langue = "en"
        self.assertEqual(services.langue_du_compte(user), "en")


class WhatsAppTests(RelancesTestCase):
    def _a_reviser(self, user):
        from quiz.models import RevisionSchedule
        from catalog.models import Subject, Tag

        RevisionSchedule.objects.create(
            profil=user.profils.first(), cursus=self.cursus, theme=Tag.objects.create(name=f"thème {user.pk}"),
            subject=Subject.objects.filter(country=self.cursus.country).first(), palier=0,
            due_at=self.maintenant.date(),
        )

    def _envoyer(self):
        backend = mock.Mock()
        with mock.patch("whatsapp.services.get_whatsapp_backend", return_value=backend):
            return whatsapp.envoyer_rappels_du_jour(), backend

    def test_un_abonne_avec_une_revision_due_recoit_son_message(self):
        user = self.eleve()
        OptIn.objects.create(user=user)
        self._a_reviser(user)

        envoyes, backend = self._envoyer()

        self.assertEqual(envoyes, 1)
        self.assertEqual(backend.send_template.call_args.kwargs["langue"], "fr")

    def test_pas_de_message_sans_abonnement_actif(self):
        user = self.eleve(abonne=False)
        OptIn.objects.create(user=user)
        self._a_reviser(user)

        self.assertEqual(self._envoyer()[0], 0)

    def test_pas_de_message_a_qui_a_deja_ete_prevenu_aujourd_hui(self):
        user = self.eleve()
        OptIn.objects.create(user=user)
        self._a_reviser(user)
        RelanceEnvoyee.objects.create(
            user=user, type=TypeRelance.RAPPEL_SEANCE, canal=CanalRelance.PUSH,
            reference=self.maintenant.astimezone(DOUALA).date().isoformat(),
        )

        self.assertEqual(self._envoyer()[0], 0)

    def test_l_accord_est_refuse_sans_numero_sur_le_compte(self):
        from rest_framework.test import APIClient
        from users.models import User

        user = User.objects.create_user(None, email="sans-numero@example.com", password="x")
        client = APIClient()
        client.force_authenticate(user=user)

        reponse = client.post("/whatsapp/opt-in/")

        self.assertEqual(reponse.status_code, 400)
        self.assertEqual(reponse.data["code"], "numero_requis")
        self.assertFalse(OptIn.objects.filter(user=user).exists())


class OrdonnanceurTests(RelancesTestCase):
    def test_les_purges_tournent_une_fois_par_nuit(self):
        with mock.patch.object(planifier_relances, "call_command") as commande:
            jour = planifier_relances.passer_une_fois(datetime(2026, 9, 28, 12, 0, tzinfo=DOUALA))
            nuit = planifier_relances.passer_une_fois(datetime(2026, 9, 28, 3, 15, tzinfo=DOUALA))

        self.assertEqual(jour["purge"], 0)
        self.assertEqual(nuit["purge"], 2)
        self.assertEqual([appel.args[0] for appel in commande.call_args_list], ["purger_invites", "purge_otp_codes"])

    def test_une_purge_en_echec_n_arrete_pas_le_tour(self):
        with mock.patch.object(planifier_relances, "call_command", side_effect=RuntimeError("base occupée")):
            resultat = planifier_relances.passer_une_fois(datetime(2026, 9, 28, 3, 15, tzinfo=DOUALA))

        self.assertEqual(resultat["purge"], 0)

    def test_le_tour_commence_par_rattraper_les_paiements(self):
        with mock.patch.object(planifier_relances, "rattraper_paiements_en_attente", return_value=3) as rattrapage:
            resultat = planifier_relances.passer_une_fois(datetime(2026, 9, 28, 12, 0, tzinfo=DOUALA))

        rattrapage.assert_called_once()
        self.assertEqual(resultat["rattrapage"], 3)
