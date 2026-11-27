"""Fin d'abonnement (voir relances.fin_abonnement) : trois jours avant, le jour même, puis rien."""
from datetime import datetime, timedelta
from unittest import mock
from zoneinfo import ZoneInfo

from django.core import mail

from payments.models import ManualPayment, ManualPaymentStatus
from quiz.models import OrigineSeance, SeanceJournaliere, StatutSeance
from subscriptions.models import Subscription
from users.models import Profil

from . import fin_abonnement
from .management.commands.planifier_relances import passer_une_fois
from .models import RelanceEnvoyee, TypeRelance
from .tests import RelancesTestCase

DOUALA = ZoneInfo("Africa/Douala")
# Un jeudi soir, dans la fenêtre d'envoi de l'ordonnanceur.
SOIR = datetime(2026, 12, 10, 17, 30, tzinfo=DOUALA)


class FinAbonnementTestCase(RelancesTestCase):
    def abonne_jusqua(self, fin, **options):
        """Un compte dont l'accès se termine à `fin`. Sans rappels demandés : ce message n'en dépend pas."""
        user = self.eleve(abonne=False, rappels=False, **options)
        abonnement = Subscription.objects.create(user=user, profil=user.profils.first(), cursus=self.cursus, expires_at=fin)
        return user, abonnement

    def types_envoyes(self, user):
        return list(RelanceEnvoyee.objects.filter(user=user).order_by("envoyee_at").values_list("type", flat=True))


class SelectionTests(FinAbonnementTestCase):
    def test_trois_jours_avant_un_message_au_compte_avec_la_date_et_le_lien_direct(self):
        user, abonnement = self.abonne_jusqua(SOIR + timedelta(days=3))

        self.assertEqual(fin_abonnement.envoyer_relances_fin_abonnement(SOIR), 1)

        message = mail.outbox[0]
        self.assertEqual(message.to, [user.email])
        self.assertEqual(message.subject, "Ton accès EduKora se termine le 13 décembre 2026")
        self.assertIn("Bonjour Awa,", message.body)
        self.assertIn("se termine le 13 décembre 2026.", message.body)
        self.assertIn(f"/abonnement?cursus={self.cursus.pk}&profil={abonnement.profil_id}", message.body)
        self.assertIn("Rien n'est prélevé automatiquement", message.body)
        self.assertNotIn("dernier message", message.body)
        self.assertEqual(self.types_envoyes(user), [TypeRelance.FIN_ABONNEMENT_1])
        html = self.assert_aux_couleurs(
            message, f"{fin_abonnement.settings.FRONTEND_URL}/abonnement?cursus={self.cursus.pk}&profil={abonnement.profil_id}",
        )
        self.assertIn("<strong>13 décembre 2026</strong>", html)

    def test_rien_avant_la_fenetre_et_une_seule_fois_dedans(self):
        user, _ = self.abonne_jusqua(SOIR + timedelta(days=4))

        self.assertEqual(fin_abonnement.envoyer_relances_fin_abonnement(SOIR), 0)
        # Le lendemain : J-3. Puis J-2, dans la fenêtre aussi : déjà parti.
        self.assertEqual(fin_abonnement.envoyer_relances_fin_abonnement(SOIR + timedelta(days=1)), 1)
        self.assertEqual(fin_abonnement.envoyer_relances_fin_abonnement(SOIR + timedelta(days=2)), 0)
        self.assertEqual(len(mail.outbox), 1)

    def test_le_premier_message_manque_a_j3_part_a_j2_pas_a_j1(self):
        self.abonne_jusqua(SOIR + timedelta(days=2))
        self.assertEqual(fin_abonnement.envoyer_relances_fin_abonnement(SOIR), 1)

        self.abonne_jusqua(SOIR + timedelta(days=1), email="autre@example.com")
        self.assertEqual(fin_abonnement.envoyer_relances_fin_abonnement(SOIR), 0)

    def test_le_jour_meme_le_dernier_message_et_plus_rien_le_lendemain(self):
        user, _ = self.abonne_jusqua(SOIR + timedelta(hours=3))

        self.assertEqual(fin_abonnement.envoyer_relances_fin_abonnement(SOIR), 1)

        message = mail.outbox[0]
        self.assertEqual(message.subject, "Dernier jour de ton accès EduKora")
        self.assertIn("se termine aujourd'hui, le 10 décembre 2026.", message.body)
        self.assertIn("C'est notre dernier message à ce sujet.", message.body)
        self.assertEqual(self.types_envoyes(user), [TypeRelance.FIN_ABONNEMENT_2])
        self.assertEqual(fin_abonnement.envoyer_relances_fin_abonnement(SOIR + timedelta(days=1)), 0)

    def test_un_acces_termine_le_matin_recoit_encore_le_message_du_jour(self):
        self.abonne_jusqua(SOIR - timedelta(hours=8))
        self.assertEqual(fin_abonnement.envoyer_relances_fin_abonnement(SOIR), 1)

    def test_les_deux_messages_se_suivent_pour_un_meme_acces(self):
        user, _ = self.abonne_jusqua(SOIR + timedelta(days=3))

        for jour in range(5):
            fin_abonnement.envoyer_relances_fin_abonnement(SOIR + timedelta(days=jour))

        self.assertEqual(self.types_envoyes(user), [TypeRelance.FIN_ABONNEMENT_1, TypeRelance.FIN_ABONNEMENT_2])

    def test_pas_d_adresse_confirmee_pas_de_message(self):
        self.abonne_jusqua(SOIR + timedelta(days=3), email_verifie=False)
        self.assertEqual(fin_abonnement.envoyer_relances_fin_abonnement(SOIR), 0)

    def test_un_acces_prolonge_ne_recoit_pas_le_dernier_message_de_l_ancienne_date(self):
        user, abonnement = self.abonne_jusqua(SOIR + timedelta(days=3))
        fin_abonnement.envoyer_relances_fin_abonnement(SOIR)

        Subscription.objects.filter(pk=abonnement.pk).update(expires_at=SOIR + timedelta(days=33))

        self.assertEqual(fin_abonnement.envoyer_relances_fin_abonnement(SOIR + timedelta(days=3)), 0)
        # À sa nouvelle échéance, l'accès a de nouveau ses deux messages.
        self.assertEqual(fin_abonnement.envoyer_relances_fin_abonnement(SOIR + timedelta(days=30)), 1)
        self.assertEqual(self.types_envoyes(user), [TypeRelance.FIN_ABONNEMENT_1, TypeRelance.FIN_ABONNEMENT_1])

    def test_un_paiement_par_transfert_en_cours_de_verification_suspend_le_message(self):
        user, abonnement = self.abonne_jusqua(SOIR + timedelta(days=3))
        ManualPayment.objects.create(
            user=user, profil=abonnement.profil, plan=self.plan, operator="MTN", amount_expected=2000, amount_declared=2000,
            payer_phone_number="677000000", transaction_reference="REF123", status=ManualPaymentStatus.PENDING,
        )

        attendu = 0 if self.plan.cursus_id == self.cursus.pk else 1
        self.assertEqual(fin_abonnement.envoyer_relances_fin_abonnement(SOIR), attendu)

    def test_examen_passe_rien_a_prolonger(self):
        self.abonne_jusqua(SOIR + timedelta(days=3))
        with mock.patch.object(fin_abonnement, "_examen_passe", return_value=True):
            self.assertEqual(fin_abonnement.envoyer_relances_fin_abonnement(SOIR), 0)

    def test_un_envoi_en_echec_n_est_pas_marque_fait(self):
        user, _ = self.abonne_jusqua(SOIR + timedelta(days=3))
        with mock.patch.object(fin_abonnement, "_envoyer_email", side_effect=RuntimeError("smtp")):
            self.assertEqual(fin_abonnement.envoyer_relances_fin_abonnement(SOIR), 0)

        self.assertEqual(self.types_envoyes(user), [])
        self.assertEqual(fin_abonnement.envoyer_relances_fin_abonnement(SOIR), 1)

    def test_dry_run_compte_sans_rien_envoyer(self):
        user, _ = self.abonne_jusqua(SOIR + timedelta(days=3))

        self.assertEqual(fin_abonnement.envoyer_relances_fin_abonnement(SOIR, dry_run=True), 1)

        self.assertEqual(mail.outbox, [])
        self.assertEqual(self.types_envoyes(user), [])


class TexteTests(FinAbonnementTestCase):
    def test_le_parent_lit_le_prenom_de_l_enfant_et_ses_seances(self):
        user, abonnement = self.abonne_jusqua(SOIR + timedelta(days=3))
        Profil.objects.filter(pk=abonnement.profil_id).update(prenom="Guyguy")
        for il_y_a in (1, 2):
            SeanceJournaliere.objects.create(
                profil=abonnement.profil, cursus=self.cursus, date=SOIR.date() - timedelta(days=il_y_a),
                origine=OrigineSeance.PARCOURS, statut=StatutSeance.TERMINEE, etapes=[],
            )
        abonnement.refresh_from_db()

        _sujet, corps, _html = fin_abonnement.composer_relance_fin_abonnement(abonnement, TypeRelance.FIN_ABONNEMENT_1)

        self.assertIn("L'accès de Guyguy à EduKora", corps)
        self.assertIn("2 séances terminées jusqu'ici.", corps)

    def test_un_prenom_qui_commence_par_une_voyelle_s_elide(self):
        _, abonnement = self.abonne_jusqua(SOIR + timedelta(days=3))
        Profil.objects.filter(pk=abonnement.profil_id).update(prenom="Étienne")
        abonnement.refresh_from_db()

        _sujet, corps, _html = fin_abonnement.composer_relance_fin_abonnement(abonnement, TypeRelance.FIN_ABONNEMENT_1)

        self.assertIn("L'accès d'Étienne à EduKora", corps)

    def test_le_titulaire_qui_etudie_lui_meme_lit_ton_acces(self):
        _, abonnement = self.abonne_jusqua(SOIR + timedelta(days=3))
        Profil.objects.filter(pk=abonnement.profil_id).update(prenom="Awa")
        abonnement.refresh_from_db()

        _sujet, corps, _html = fin_abonnement.composer_relance_fin_abonnement(abonnement, TypeRelance.FIN_ABONNEMENT_1)

        self.assertIn("Ton accès à EduKora", corps)
        self.assertNotIn("L'accès d'Awa", corps)
        # Aucune séance terminée : pas de phrase à zéro.
        self.assertNotIn("séance", corps)

    def test_en_anglais_pour_un_compte_en_anglais(self):
        user, abonnement = self.abonne_jusqua(SOIR + timedelta(days=3))
        type(user).objects.filter(pk=user.pk).update(langue="en")
        abonnement.refresh_from_db()

        sujet, corps, _html = fin_abonnement.composer_relance_fin_abonnement(abonnement, TypeRelance.FIN_ABONNEMENT_1)

        self.assertEqual(sujet, "Your EduKora access ends on 13 December 2026")
        self.assertIn("Hello Awa,", corps)
        self.assertIn("Nothing is charged automatically", corps)


class PlanificateurTests(FinAbonnementTestCase):
    def test_le_message_part_dans_la_fenetre_de_fin_d_apres_midi(self):
        self.abonne_jusqua(SOIR + timedelta(days=3))

        matin = SOIR.replace(hour=9)
        self.assertEqual(passer_une_fois(matin)["fin_abonnement"], 0)
        self.assertEqual(passer_une_fois(SOIR)["fin_abonnement"], 1)
        self.assertEqual(passer_une_fois(SOIR.replace(hour=18))["fin_abonnement"], 0)
        self.assertEqual(len(mail.outbox), 1)
