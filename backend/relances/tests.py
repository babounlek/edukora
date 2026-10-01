"""Relances e-mail : rappel quotidien, paiement non abouti, désabonnement."""

from datetime import timedelta
from unittest import mock

from django.core import mail
from django.test import TestCase
from django.utils import timezone

from catalog.models import Cursus
from payments.models import ManualPayment, ManualPaymentStatus, StatutTransaction, Transaction
from quiz.models import OrigineSeance, SeanceJournaliere, StatutSeance
from subscriptions.models import Plan, Subscription
from users.models import User

from . import services
from .models import RelanceEnvoyee, TypeRelance


class RelancesTestCase(TestCase):
    def setUp(self):
        self.cursus = Cursus.objects.filter(country__actif=True).first()
        self.plan = Plan.objects.filter(cursus=self.cursus).first() or Plan.objects.first()
        self.maintenant = timezone.now()
        self._telephone = 677500000

    def eleve(self, *, rappels=True, email_verifie=True, abonne=True, cursus=True, email="eleve@example.com"):
        self._telephone += 1
        user = User.objects.create_user(
            phone_number=str(self._telephone), password="x", email=f"{self._telephone}-{email}",
            email_verified=email_verifie, full_name="Awa Mballa", rappels_actifs=rappels,
        )
        if cursus:
            user.cursus_prepare = self.cursus
            user.save(update_fields=["cursus_prepare"])
        if abonne:
            Subscription.objects.create(
                user=user, profil=user.profils.first(), cursus=self.cursus,
                expires_at=self.maintenant + timedelta(days=30),
            )
        return user

    def transaction(self, user, statut, age):
        transaction = Transaction.objects.create(
            user=user, profil=user.profils.first(), plan=self.plan, amount=5000, phone_number="677000000", status=statut,
        )
        Transaction.objects.filter(pk=transaction.pk).update(created_at=self.maintenant - age)
        transaction.refresh_from_db()
        return transaction


class RappelSeanceTests(RelancesTestCase):
    def test_envoie_a_l_eleve_eligible_avec_un_lien_de_desabonnement(self):
        user = self.eleve()

        envoyes = services.envoyer_rappels_seance()

        self.assertEqual(envoyes, 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, [user.email])
        self.assertIn("Bonjour Awa,", message.body)
        self.assertIn("/relances/desabonner/", message.body)
        self.assertIn(f"/{self.cursus.country.code.lower()}", message.body)

    def test_ne_part_qu_une_fois_par_jour(self):
        self.eleve()
        services.envoyer_rappels_seance()
        self.assertEqual(services.envoyer_rappels_seance(), 0)
        self.assertEqual(len(mail.outbox), 1)

    def test_jamais_sans_consentement_ni_email_confirme_ni_abonnement(self):
        self.eleve(rappels=False)
        self.eleve(email_verifie=False)
        self.eleve(abonne=False)
        self.eleve(cursus=False)

        self.assertEqual(services.envoyer_rappels_seance(), 0)
        self.assertEqual(mail.outbox, [])

    def test_pas_de_rappel_a_qui_a_deja_fait_sa_seance_aujourd_hui(self):
        user = self.eleve()
        SeanceJournaliere.objects.create(
            profil=user.profils.first(), cursus=self.cursus, date=timezone.localdate(), origine=OrigineSeance.DIAGNOSTIC,
            statut=StatutSeance.TERMINEE,
        )
        self.assertEqual(services.envoyer_rappels_seance(), 0)

    def test_le_rappel_ne_cree_aucune_seance(self):
        self.eleve()
        services.envoyer_rappels_seance()
        self.assertFalse(SeanceJournaliere.objects.exists())

    def test_la_serie_est_mentionnee_a_partir_de_deux_jours(self):
        user = self.eleve()
        for decalage in (1, 2, 3):
            SeanceJournaliere.objects.create(
                profil=user.profils.first(), cursus=self.cursus, date=timezone.localdate() - timedelta(days=decalage),
                origine=OrigineSeance.DIAGNOSTIC, statut=StatutSeance.TERMINEE,
            )
        services.envoyer_rappels_seance()
        self.assertIn("Ta série est à 3 jours de suite.", mail.outbox[0].body)

    def test_un_envoi_en_echec_n_est_pas_marque_fait_et_les_autres_partent(self):
        self.eleve()
        deuxieme = self.eleve()
        vrai_envoi = services._envoyer_email
        appels = []

        def envoi_capricieux(user, sujet, corps):
            appels.append(user.pk)
            if len(appels) == 1:
                raise OSError("SMTP indisponible")
            return vrai_envoi(user, sujet, corps)

        with mock.patch.object(services, "_envoyer_email", side_effect=envoi_capricieux):
            envoyes = services.envoyer_rappels_seance()

        self.assertEqual(envoyes, 1)
        self.assertEqual(RelanceEnvoyee.objects.count(), 1)
        # L'élève resté sans message est retenté à la prochaine exécution.
        self.assertEqual(services.envoyer_rappels_seance(), 1)
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn(deuxieme.email, [m.to[0] for m in mail.outbox])

    def test_dry_run_ne_compte_que(self):
        self.eleve()
        self.assertEqual(services.envoyer_rappels_seance(dry_run=True), 1)
        self.assertEqual(mail.outbox, [])
        self.assertFalse(RelanceEnvoyee.objects.exists())


class RelancePaiementTests(RelancesTestCase):
    def test_premier_message_apres_deux_heures_puis_dernier_apres_soixante_douze(self):
        user = self.eleve(abonne=False, rappels=False)
        transaction = self.transaction(user, StatutTransaction.FAILED, timedelta(hours=3))

        self.assertEqual(services.envoyer_relances_paiement(self.maintenant), 1)
        self.assertEqual(services.envoyer_relances_paiement(self.maintenant), 0)
        self.assertIn("n'a pas abouti", mail.outbox[0].body)
        self.assertIn(f"/abonnement?cursus={self.plan.cursus_id}", mail.outbox[0].body)

        plus_tard = self.maintenant + timedelta(hours=80)
        self.assertEqual(services.envoyer_relances_paiement(plus_tard), 1)
        self.assertIn("dernier message", mail.outbox[1].body)

        # Jamais un troisième message pour la même tentative.
        self.assertEqual(services.envoyer_relances_paiement(plus_tard + timedelta(hours=1)), 0)
        self.assertEqual(
            set(RelanceEnvoyee.objects.filter(user=user).values_list("type", flat=True)),
            {TypeRelance.PAIEMENT_ABANDONNE_1, TypeRelance.PAIEMENT_ABANDONNE_2},
        )
        self.assertEqual(RelanceEnvoyee.objects.filter(reference=str(transaction.pk)).count(), 2)

    def test_pas_de_relance_trop_tot(self):
        user = self.eleve(abonne=False, rappels=False)
        self.transaction(user, StatutTransaction.FAILED, timedelta(minutes=30))
        self.assertEqual(services.envoyer_relances_paiement(self.maintenant), 0)

    def test_un_paiement_en_cours_de_confirmation_n_est_pas_relance(self):
        user = self.eleve(abonne=False, rappels=False)
        self.transaction(user, StatutTransaction.PENDING, timedelta(minutes=40))
        self.assertIsNone(services.paiement_a_reprendre(user, self.maintenant))

    def test_un_paiement_reste_en_attente_depuis_longtemps_est_relance(self):
        user = self.eleve(abonne=False, rappels=False)
        self.transaction(user, StatutTransaction.PENDING, timedelta(hours=3))
        self.assertEqual(services.envoyer_relances_paiement(self.maintenant), 1)
        self.assertIn("n'a pas été confirmé", mail.outbox[0].body)

    def test_jamais_a_qui_a_paye_ou_est_abonne_ou_attend_la_validation_d_un_paiement_manuel(self):
        paye = self.eleve(abonne=False, rappels=False)
        self.transaction(paye, StatutTransaction.FAILED, timedelta(hours=5))
        self.transaction(paye, StatutTransaction.SUCCESSFUL, timedelta(hours=4))
        abonne = self.eleve(abonne=True, rappels=False)
        self.transaction(abonne, StatutTransaction.FAILED, timedelta(hours=5))
        manuel = self.eleve(abonne=False, rappels=False)
        self.transaction(manuel, StatutTransaction.FAILED, timedelta(hours=5))
        ManualPayment.objects.bulk_create([
            ManualPayment(
                user=manuel, profil=manuel.profils.first(), plan=self.plan, operator="ORANGE", amount_declared=5000,
                amount_expected=5000, status=ManualPaymentStatus.PENDING,
            ),
        ])

        self.assertEqual(services.envoyer_relances_paiement(self.maintenant), 0)

    def test_jamais_sans_email_confirme(self):
        user = self.eleve(abonne=False, rappels=False, email_verifie=False)
        self.transaction(user, StatutTransaction.FAILED, timedelta(hours=5))
        self.assertEqual(services.envoyer_relances_paiement(self.maintenant), 0)

    def test_une_tentative_trop_ancienne_n_est_plus_relancee(self):
        user = self.eleve(abonne=False, rappels=False)
        self.transaction(user, StatutTransaction.FAILED, timedelta(days=9))
        self.assertEqual(services.envoyer_relances_paiement(self.maintenant), 0)


class DesabonnementTests(RelancesTestCase):
    def test_le_lien_coupe_les_rappels_sans_connexion(self):
        user = self.eleve()

        reponse = self.client.get(f"/relances/desabonner/{services.jeton_desabonnement(user)}/")

        self.assertEqual(reponse.status_code, 200)
        user.refresh_from_db()
        self.assertFalse(user.rappels_actifs)

    def test_un_jeton_altere_est_refuse_et_ne_touche_personne(self):
        user = self.eleve()
        jeton = services.jeton_desabonnement(user)

        reponse = self.client.get(f"/relances/desabonner/{jeton[:-3]}xyz/")

        self.assertEqual(reponse.status_code, 400)
        user.refresh_from_db()
        self.assertTrue(user.rappels_actifs)

    def test_un_jeton_ne_vaut_que_pour_son_eleve(self):
        un, deux = self.eleve(), self.eleve()
        self.client.get(f"/relances/desabonner/{services.jeton_desabonnement(un)}/")
        deux.refresh_from_db()
        self.assertTrue(deux.rappels_actifs)


class ProfilRappelsTests(RelancesTestCase):
    def test_activer_les_rappels_exige_un_email_confirme(self):
        from rest_framework.test import APIClient

        client = APIClient()
        sans_email = self.eleve(rappels=False, email_verifie=False)
        client.force_authenticate(user=sans_email)
        self.assertEqual(client.patch("/auth/me/", {"rappels_actifs": True}, format="json").status_code, 400)

        avec_email = self.eleve(rappels=False, email_verifie=True)
        client.force_authenticate(user=avec_email)
        reponse = client.patch("/auth/me/", {"rappels_actifs": True}, format="json")
        self.assertEqual(reponse.status_code, 200)
        self.assertTrue(reponse.data["rappels_actifs"])

    def test_ecarter_puis_rouvrir_l_invitation(self):
        from rest_framework.test import APIClient

        client = APIClient()
        user = self.eleve(rappels=False)
        client.force_authenticate(user=user)

        ecartee = client.patch("/auth/me/", {"rappels_invite_refusee": True}, format="json")
        self.assertTrue(ecartee.data["rappels_invite_refusee"])
        rouverte = client.patch("/auth/me/", {"rappels_invite_refusee": False}, format="json")
        self.assertFalse(rouverte.data["rappels_invite_refusee"])
