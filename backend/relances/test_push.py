"""Notifications push : abonnement, heure habituelle, envoi une fois par jour (voir relances.push)."""

from datetime import datetime, timedelta
from unittest import mock
from zoneinfo import ZoneInfo

from django.core import mail
from django.core.management import call_command
from django.test import override_settings
from rest_framework.test import APIClient

from catalog.models import Subject
from quiz.models import (
    JourXP, ModeQuiz, OrigineSeance, QuizAnswer, QuizQuestion, QuizSession, SeanceJournaliere, StatutSeance,
)
from quiz.tests import _make_competence_item

from . import push
from .management.commands.planifier_relances import passer_une_fois
from .models import AbonnementPush, CanalRelance, RelanceEnvoyee, TypeRelance
from .tests import RelancesTestCase

DOUALA = ZoneInfo("Africa/Douala")
CLES_VAPID = {"VAPID_PUBLIC_KEY": "cle-publique", "VAPID_PRIVATE_KEY": "cle-privee", "VAPID_CLAIM_EMAIL": "contact@example.com"}

SOIR = datetime(2026, 9, 28, 18, 30, tzinfo=DOUALA)


class PushTestCase(RelancesTestCase):
    def appareil(self, user, endpoint="https://push.example.com/abc"):
        return AbonnementPush.objects.create(user=user, endpoint=endpoint, p256dh="p256dh", auth="auth")

    def seance_terminee(self, user, quand):
        return SeanceJournaliere.objects.create(
            profil=user.profils.first(), cursus=self.cursus, date=quand.astimezone(DOUALA).date(),
            origine=OrigineSeance.DIAGNOSTIC, ordre=1, statut=StatutSeance.TERMINEE, termine_at=quand,
        )


@override_settings(**CLES_VAPID)
class EnvoiTests(PushTestCase):
    def envoyer(self, maintenant=SOIR, **kw):
        with mock.patch("relances.push._webpush") as webpush:
            return push.envoyer_rappels_push(maintenant, **kw), webpush

    def test_un_appareil_abonne_recoit_le_rappel_a_l_heure_par_defaut(self):
        user = self.eleve(rappels=False)
        self.appareil(user)
        envoyes, webpush = self.envoyer()
        self.assertEqual(envoyes, 1)
        charge = webpush.call_args.args[1]
        self.assertIn("séance du jour", charge["title"])
        self.assertTrue(charge["url"].startswith("/"))
        self.assertTrue(RelanceEnvoyee.objects.filter(user=user, canal=CanalRelance.PUSH).exists())

    def test_un_seul_message_par_jour_meme_avec_deux_appareils_et_deux_tours(self):
        user = self.eleve()
        self.appareil(user, "https://push.example.com/1")
        self.appareil(user, "https://push.example.com/2")
        envoyes, webpush = self.envoyer()
        self.assertEqual((envoyes, webpush.call_count), (1, 2))
        envoyes, webpush = self.envoyer(SOIR + timedelta(hours=1))
        self.assertEqual((envoyes, webpush.call_count), (0, 0))

    def test_rien_avant_l_heure_ni_apres_le_retard_maximal(self):
        user = self.eleve()
        self.appareil(user)
        self.assertEqual(self.envoyer(SOIR.replace(hour=9))[0], 0)
        self.assertEqual(self.envoyer(SOIR.replace(hour=22))[0], 0)

    def test_sans_cles_vapid_rien_ne_part(self):
        user = self.eleve()
        self.appareil(user)
        with override_settings(VAPID_PUBLIC_KEY="", VAPID_PRIVATE_KEY=""):
            envoyes, webpush = self.envoyer()
        self.assertEqual((envoyes, webpush.call_count), (0, 0))

    def test_pas_de_rappel_sans_abonnement_payant_ni_sans_appareil(self):
        self.appareil(self.eleve(abonne=False), "https://push.example.com/a")
        self.eleve()  # abonné mais sans appareil
        self.assertEqual(self.envoyer()[0], 0)

    def test_pas_de_rappel_quand_la_journee_est_deja_faite(self):
        fait = self.eleve()
        self.appareil(fait, "https://push.example.com/a")
        self.seance_terminee(fait, SOIR - timedelta(hours=3))
        objectif = self.eleve()
        self.appareil(objectif, "https://push.example.com/b")
        JourXP.objects.create(profil=objectif.profils.first(), jour=SOIR.date(), xp=20, objectif=20, atteint=True)
        self.assertEqual(self.envoyer()[0], 0)

    def test_pas_de_push_quand_l_email_du_jour_est_deja_parti(self):
        user = self.eleve()
        self.appareil(user)
        RelanceEnvoyee.objects.create(
            user=user, type=TypeRelance.RAPPEL_SEANCE, reference=SOIR.date().isoformat(), canal=CanalRelance.EMAIL,
        )
        self.assertEqual(self.envoyer()[0], 0)

    def test_un_appareil_disparu_est_oublie_et_la_trace_retiree_pour_retenter(self):
        from pywebpush import WebPushException

        user = self.eleve()
        self.appareil(user)
        reponse = mock.Mock(status_code=410)
        with mock.patch("relances.push._webpush", side_effect=WebPushException("gone", response=reponse)):
            self.assertEqual(push.envoyer_rappels_push(SOIR), 0)
        self.assertFalse(AbonnementPush.objects.exists())
        self.assertFalse(RelanceEnvoyee.objects.filter(canal=CanalRelance.PUSH).exists())

    def test_une_panne_passagere_garde_l_abonnement_et_permet_de_retenter(self):
        user = self.eleve()
        self.appareil(user)
        with mock.patch("relances.push._webpush", side_effect=RuntimeError("réseau")):
            self.assertEqual(push.envoyer_rappels_push(SOIR), 0)
        self.assertEqual(AbonnementPush.objects.count(), 1)
        envoyes, _ = self.envoyer(SOIR + timedelta(hours=1))
        self.assertEqual(envoyes, 1)

    def test_dry_run_compte_sans_rien_envoyer(self):
        user = self.eleve()
        self.appareil(user)
        envoyes, webpush = self.envoyer(dry_run=True)
        self.assertEqual((envoyes, webpush.call_count), (1, 0))
        self.assertFalse(RelanceEnvoyee.objects.exists())

    def test_le_tour_de_l_ordonnanceur_envoie_le_push_puis_pas_l_email(self):
        user = self.eleve(rappels=True)
        self.appareil(user)
        with mock.patch("relances.push._webpush"):
            resultat = passer_une_fois(SOIR)
        self.assertEqual((resultat["push"], resultat["rappel"]), (1, 0))
        self.assertEqual(mail.outbox, [])


class HeureHabituelleTests(PushTestCase):
    def activite(self, user, jour_decalage, heure):
        quand = (SOIR - timedelta(days=jour_decalage)).replace(hour=heure, minute=10)
        self.seance_terminee_ordre = getattr(self, "seance_terminee_ordre", 0) + 1
        return SeanceJournaliere.objects.create(
            profil=user.profils.first(), cursus=self.cursus, date=quand.date(), origine=OrigineSeance.DIAGNOSTIC,
            ordre=self.seance_terminee_ordre, statut=StatutSeance.TERMINEE, termine_at=quand,
        )

    def test_sans_assez_d_historique_c_est_l_heure_par_defaut(self):
        user = self.eleve()
        self.activite(user, 1, 7)
        self.activite(user, 2, 7)
        self.assertEqual(push.heure_habituelle(user.profils.first(), SOIR), push.HEURE_PAR_DEFAUT)

    def test_l_heure_la_plus_frequente_l_emporte(self):
        user = self.eleve()
        for decalage, heure in ((1, 20), (2, 20), (3, 20), (4, 16), (5, 16)):
            self.activite(user, decalage, heure)
        self.assertEqual(push.heure_habituelle(user.profils.first(), SOIR), 20)

    def test_a_egalite_la_plus_tardive(self):
        user = self.eleve()
        for decalage, heure in ((1, 16), (2, 16), (3, 20), (4, 20), (5, 12), (6, 12)):
            self.activite(user, decalage, heure)
        self.assertEqual(push.heure_habituelle(user.profils.first(), SOIR), 20)

    def test_une_journee_de_quarante_reponses_ne_pese_qu_une_fois(self):
        user = self.eleve()
        profil = user.profils.first()
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        session = QuizSession.objects.create(profil=profil, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        for i in range(10):
            item = _make_competence_item(subject, self.cursus, numero=f"h{i}")
            reponse = QuizAnswer.objects.create(
                quiz_question=QuizQuestion.objects.create(session=session, competence_item=item, ordre=i + 1),
            )
            QuizAnswer.objects.filter(pk=reponse.pk).update(answered_at=SOIR.replace(hour=9) - timedelta(days=1))
        self.activite(user, 2, 20)
        self.activite(user, 3, 20)
        self.assertEqual(push.heure_habituelle(profil, SOIR), 20)


@override_settings(**CLES_VAPID)
class ComposerTests(PushTestCase):
    def test_une_serie_a_prolonger_est_annoncee_sans_reproche(self):
        user = self.eleve()
        for decalage in (1, 2, 3):
            self.seance_terminee(user, SOIR - timedelta(days=decalage))
        charge = push.composer_push(user, SOIR)
        self.assertIn("3 jours", charge["title"])
        self.assertIn("XP", charge["body"])

    def test_sans_serie_c_est_la_seance(self):
        charge = push.composer_push(self.eleve(), SOIR)
        self.assertIn("séance du jour", charge["title"])
        self.assertIn("Awa", charge["title"])


@override_settings(**CLES_VAPID)
class ApiTests(PushTestCase):
    def setUp(self):
        super().setUp()
        self.user = self.eleve()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.corps = {"endpoint": "https://push.example.com/xyz", "keys": {"p256dh": "kp", "auth": "ka"}}

    def test_la_cle_publique_est_servie_quand_le_push_est_configure(self):
        self.assertEqual(self.client.get("/relances/push/cle/").json(), {"actif": True, "cle": "cle-publique"})

    def test_sans_configuration_le_push_est_declare_inactif(self):
        with override_settings(VAPID_PUBLIC_KEY="", VAPID_PRIVATE_KEY=""):
            self.assertEqual(self.client.get("/relances/push/cle/").json(), {"actif": False, "cle": ""})
            self.assertEqual(self.client.post("/relances/push/abonner/", self.corps, format="json").status_code, 409)

    def test_abonner_enregistre_l_appareil(self):
        reponse = self.client.post("/relances/push/abonner/", self.corps, format="json")
        self.assertEqual(reponse.status_code, 201)
        abonnement = AbonnementPush.objects.get()
        self.assertEqual((abonnement.user, abonnement.p256dh, abonnement.auth), (self.user, "kp", "ka"))

    def test_se_reabonner_ne_duplique_pas_et_change_de_compte(self):
        self.client.post("/relances/push/abonner/", self.corps, format="json")
        autre = self.eleve()
        client = APIClient()
        client.force_authenticate(user=autre)
        client.post("/relances/push/abonner/", {**self.corps, "keys": {"p256dh": "k2", "auth": "a2"}}, format="json")
        abonnement = AbonnementPush.objects.get()
        self.assertEqual((abonnement.user, abonnement.p256dh), (autre, "k2"))

    def test_un_abonnement_mal_forme_est_refuse(self):
        for corps in (
            {}, {"endpoint": "http://pas-https", "keys": {"p256dh": "a", "auth": "b"}},
            {"endpoint": "https://x.example.com/", "keys": {}}, {"endpoint": "https://x.example.com/", "keys": {"p256dh": "a" * 201, "auth": "b"}},
            {"endpoint": 12, "keys": {"p256dh": "a", "auth": "b"}},
        ):
            self.assertEqual(self.client.post("/relances/push/abonner/", corps, format="json").status_code, 400, corps)
        self.assertFalse(AbonnementPush.objects.exists())

    def test_desabonner_ne_touche_que_ses_propres_appareils(self):
        autre = self.eleve()
        self.appareil(autre, "https://push.example.com/autre")
        self.client.post("/relances/push/abonner/", self.corps, format="json")
        self.client.post("/relances/push/desabonner/", {"endpoint": "https://push.example.com/autre"}, format="json")
        self.assertEqual(AbonnementPush.objects.count(), 2)
        self.client.post("/relances/push/desabonner/", {"endpoint": self.corps["endpoint"]}, format="json")
        self.assertEqual(list(AbonnementPush.objects.values_list("endpoint", flat=True)), ["https://push.example.com/autre"])

    def test_il_faut_etre_connecte(self):
        anonyme = APIClient()
        self.assertEqual(anonyme.get("/relances/push/cle/").status_code, 401)
        self.assertEqual(anonyme.post("/relances/push/abonner/", self.corps, format="json").status_code, 401)


class CommandesTests(PushTestCase):
    def test_generer_cles_vapid_donne_une_paire_utilisable(self):
        from io import StringIO

        from py_vapid import Vapid

        sortie = StringIO()
        call_command("generer_cles_vapid", stdout=sortie)
        lignes = dict(l.split("=", 1) for l in sortie.getvalue().splitlines() if l.startswith("VAPID_"))
        self.assertEqual(len(lignes["VAPID_PUBLIC_KEY"]), 87)
        # La clé privée se recharge, et signe : c'est ce que fait pywebpush au moment d'envoyer.
        signature = Vapid.from_string(lignes["VAPID_PRIVATE_KEY"]).sign({"sub": "mailto:a@b.cc", "aud": "https://fcm.googleapis.com"})
        self.assertIn("Authorization", signature)

    def test_envoyer_relances_seulement_push(self):
        from io import StringIO

        sortie = StringIO()
        call_command("envoyer_relances", "--seulement", "push", "--dry-run", stdout=sortie)
        self.assertIn("rappel(s) push", sortie.getvalue())
        self.assertNotIn("rappel(s) de séance", sortie.getvalue())
