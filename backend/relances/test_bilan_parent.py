"""Bilan de la semaine envoyé au parent (voir relances.bilan_parent)."""

from datetime import datetime, timedelta
from unittest import mock
from zoneinfo import ZoneInfo

from django.core import mail
from django.core.management import call_command
from rest_framework.test import APIClient

from quiz.models import JourXP, OrigineSeance, SeanceJournaliere, StatutSeance
from subscriptions.models import Subscription
from users.models import Profil

from . import bilan_parent
from .management.commands.planifier_relances import passer_une_fois
from .models import RelanceEnvoyee, TypeRelance
from .tests import RelancesTestCase

DOUALA = ZoneInfo("Africa/Douala")
# Dimanche 27 septembre 2026, 18 h 30 à Douala - semaine ISO 39.
DIMANCHE = datetime(2026, 9, 27, 18, 30, tzinfo=DOUALA)


class BilanParentTestCase(RelancesTestCase):
    def parent(self, **kw):
        user = self.eleve(**kw)
        user.bilan_parent_actif = True
        user.save(update_fields=["bilan_parent_actif"])
        return user

    def seance(self, user, jours_avant, ordre=1):
        quand = DIMANCHE - timedelta(days=jours_avant)
        return SeanceJournaliere.objects.create(
            profil=user.profils.first(), cursus=self.cursus, date=quand.date(), origine=OrigineSeance.DIAGNOSTIC,
            ordre=ordre, statut=StatutSeance.TERMINEE, termine_at=quand,
        )

    def activer_abonnement_a(self, user):
        # Les abonnements du fixture expirent dans 30 jours à partir de « maintenant » réel : on
        # les replace autour de DIMANCHE pour que le bilan soit calculé sur la bonne semaine.
        Subscription.objects.filter(user=user).update(
            created_at=DIMANCHE - timedelta(days=60), expires_at=DIMANCHE + timedelta(days=30),
        )


class ComposerTests(BilanParentTestCase):
    def test_un_profil_actif_donne_ses_faits_sans_jugement(self):
        user = self.parent()
        self.activer_abonnement_a(user)
        self.seance(user, 1)
        self.seance(user, 3, ordre=2)
        JourXP.objects.create(profil=user.profils.first(), jour=DIMANCHE.date() - timedelta(days=1), xp=40, objectif=20, atteint=True)

        sujet, corps = bilan_parent.composer_bilan_parent(user, DIMANCHE)

        self.assertEqual(sujet, "Bilan de la semaine de Awa")
        self.assertIn("2 jours de révision sur 7", corps)
        self.assertIn("2 séances", corps)
        self.assertIn("40 points", corps)
        self.assertIn("/relances/desabonner-bilan/", corps)
        self.assertNotIn("%", corps.split("Voici")[1].split("Ouvrir")[0].replace("de réussite", ""))

    def test_une_semaine_sans_revision_est_dite_simplement(self):
        user = self.parent()
        self.activer_abonnement_a(user)
        _, corps = bilan_parent.composer_bilan_parent(user, DIMANCHE)
        self.assertIn("n'a pas révisé cette semaine", corps)
        self.assertIn("25 minutes", corps)
        self.assertNotIn("jours de révision sur 7", corps)

    def test_un_compte_famille_regroupe_ses_profils_en_un_seul_message(self):
        user = self.parent()
        self.activer_abonnement_a(user)
        self.seance(user, 1)
        second = Profil.objects.create(compte=user, prenom="Junior", ordre=1)
        Subscription.objects.create(
            user=user, profil=second, cursus=self.cursus,
            created_at=DIMANCHE - timedelta(days=60), expires_at=DIMANCHE + timedelta(days=30),
        )
        sujet, corps = bilan_parent.composer_bilan_parent(user, DIMANCHE)
        self.assertEqual(sujet, "Bilan de la semaine de tes enfants")
        self.assertIn("■ Junior", corps)
        self.assertIn("Junior n'a pas révisé", corps)

    def test_un_profil_sans_abonnement_actif_est_ignore(self):
        user = self.parent(abonne=False)
        self.assertIsNone(bilan_parent.composer_bilan_parent(user, DIMANCHE))

    def test_les_themes_consolides_sont_cites(self):
        user = self.parent()
        self.activer_abonnement_a(user)
        bilan = {
            "a_de_l_activite": True, "jours_actifs": 3, "seances": 3, "questions": 20, "taux_reussite": 80,
            "themes_consolides": [{"theme": "Suites", "subject_label": "Maths"}], "xp": 0, "serie": 4,
        }
        with mock.patch("relances.bilan_parent.bilan_du_profil", return_value=bilan):
            _, corps = bilan_parent.composer_bilan_parent(user, DIMANCHE)
        self.assertIn("Thèmes consolidés : Suites (Maths).", corps)
        self.assertIn("Série en cours : 4 jours de suite.", corps)
        self.assertIn("20 questions (80 % de réussite)", corps)


class EnvoiTests(BilanParentTestCase):
    def test_le_bilan_part_une_seule_fois_par_semaine(self):
        user = self.parent()
        self.activer_abonnement_a(user)
        self.assertEqual(bilan_parent.envoyer_bilans_parent(DIMANCHE), 1)
        self.assertEqual(bilan_parent.envoyer_bilans_parent(DIMANCHE + timedelta(hours=1)), 0)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [user.email])
        self.assertTrue(RelanceEnvoyee.objects.filter(type=TypeRelance.BILAN_PARENT, reference="2026-W39").exists())

    def test_la_semaine_suivante_il_repart(self):
        user = self.parent()
        self.activer_abonnement_a(user)
        bilan_parent.envoyer_bilans_parent(DIMANCHE)
        self.assertEqual(bilan_parent.envoyer_bilans_parent(DIMANCHE + timedelta(days=7)), 1)

    def test_rien_sans_demande_ni_adresse_confirmee(self):
        sans_demande = self.eleve()
        self.activer_abonnement_a(sans_demande)
        non_confirme = self.parent(email_verifie=False)
        self.activer_abonnement_a(non_confirme)
        self.assertEqual(bilan_parent.envoyer_bilans_parent(DIMANCHE), 0)

    def test_un_envoi_rate_est_retente(self):
        user = self.parent()
        self.activer_abonnement_a(user)
        with mock.patch("relances.bilan_parent._envoyer_email", side_effect=OSError("SMTP")):
            self.assertEqual(bilan_parent.envoyer_bilans_parent(DIMANCHE), 0)
        self.assertFalse(RelanceEnvoyee.objects.filter(type=TypeRelance.BILAN_PARENT).exists())
        self.assertEqual(bilan_parent.envoyer_bilans_parent(DIMANCHE + timedelta(hours=1)), 1)

    def test_dry_run_compte_sans_envoyer(self):
        user = self.parent()
        self.activer_abonnement_a(user)
        self.assertEqual(bilan_parent.envoyer_bilans_parent(DIMANCHE, dry_run=True), 1)
        self.assertEqual(mail.outbox, [])

    def test_l_ordonnanceur_n_envoie_que_le_dimanche_en_fin_d_apres_midi(self):
        user = self.parent()
        self.activer_abonnement_a(user)
        samedi = DIMANCHE - timedelta(days=1)
        self.assertEqual(passer_une_fois(samedi)["bilan"], 0)
        self.assertEqual(passer_une_fois(DIMANCHE.replace(hour=9))["bilan"], 0)
        self.assertEqual(passer_une_fois(DIMANCHE)["bilan"], 1)

    def test_la_commande_manuelle_a_son_option(self):
        from io import StringIO

        sortie = StringIO()
        call_command("envoyer_relances", "--seulement", "bilan", "--dry-run", stdout=sortie)
        self.assertIn("bilan(s) de la semaine", sortie.getvalue())


class DesabonnementEtReglageTests(BilanParentTestCase):
    def test_le_lien_coupe_le_bilan_sans_connexion(self):
        user = self.parent()
        reponse = self.client.get(f"/relances/desabonner-bilan/{bilan_parent.jeton_desabonnement_bilan(user)}/")
        self.assertEqual(reponse.status_code, 200)
        user.refresh_from_db()
        self.assertFalse(user.bilan_parent_actif)

    def test_un_jeton_altere_est_refuse(self):
        reponse = self.client.get("/relances/desabonner-bilan/faux-jeton/")
        self.assertEqual(reponse.status_code, 400)

    def test_le_jeton_des_rappels_ne_coupe_pas_le_bilan(self):
        from .services import jeton_desabonnement

        user = self.parent()
        reponse = self.client.get(f"/relances/desabonner-bilan/{jeton_desabonnement(user)}/")
        self.assertEqual(reponse.status_code, 400)
        user.refresh_from_db()
        self.assertTrue(user.bilan_parent_actif)

    def test_l_activation_exige_une_adresse_confirmee(self):
        user = self.eleve(email_verifie=False)
        client = APIClient()
        client.force_authenticate(user=user)
        reponse = client.patch("/auth/me/", {"bilan_parent_actif": True}, format="json")
        self.assertEqual(reponse.status_code, 400)

    def test_l_activation_marche_avec_une_adresse_confirmee_et_s_expose(self):
        user = self.eleve()
        client = APIClient()
        client.force_authenticate(user=user)
        reponse = client.patch("/auth/me/", {"bilan_parent_actif": True}, format="json")
        self.assertEqual(reponse.status_code, 200)
        self.assertTrue(reponse.json()["bilan_parent_actif"])
        user.refresh_from_db()
        self.assertTrue(user.bilan_parent_actif)

    def test_le_reglage_est_reserve_au_mode_parent(self):
        user = self.eleve()
        client = APIClient()
        client.force_authenticate(user=user)
        with mock.patch("users.views.exiger_mode_parent") as garde:
            from rest_framework.response import Response

            garde.return_value = Response({"error": "Cette action est réservée au parent."}, status=403)
            reponse = client.patch("/auth/me/", {"bilan_parent_actif": True}, format="json")
        self.assertEqual(reponse.status_code, 403)
        user.refresh_from_db()
        self.assertFalse(user.bilan_parent_actif)
