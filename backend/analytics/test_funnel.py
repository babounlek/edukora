"""Entonnoir inscription -> paiement (voir analytics.funnel)."""

from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Cursus
from payments.models import StatutTransaction, Transaction
from quiz.models import OrigineSeance, SeanceJournaliere, StatutSeance
from subscriptions.models import Plan
from users.models import User

from .funnel import entonnoir


class EntonnoirTests(TestCase):
    def setUp(self):
        self.cursus = Cursus.objects.first()
        self.plan = Plan.objects.first()
        self.maintenant = timezone.now()

    def eleve(self, telephone, *, jours=20, cursus=None, **extra):
        user = User.objects.create_user(phone_number=telephone, password="x", **extra)
        User.objects.filter(pk=user.pk).update(
            date_joined=self.maintenant - timedelta(days=jours), cursus_prepare=cursus,
        )
        user.refresh_from_db()
        return user

    def seance(self, user, *, termine, jours_apres_inscription=0, ordre=1):
        quand = user.date_joined + timedelta(days=jours_apres_inscription)
        return SeanceJournaliere.objects.create(
            profil=user.profils.first(), cursus=self.cursus, date=quand.date(),
            origine=OrigineSeance.DIAGNOSTIC, ordre=ordre,
            statut=StatutSeance.TERMINEE if termine else StatutSeance.PROPOSEE,
            termine_at=quand if termine else None,
        )

    def paiement(self, user, statut, *, age=timedelta(days=1)):
        transaction = Transaction.objects.create(
            user=user, profil=user.profils.first(), plan=self.plan, amount=5000, phone_number="677000000", status=statut,
        )
        Transaction.objects.filter(pk=transaction.pk).update(created_at=self.maintenant - age)
        return transaction

    def etape(self, rapport, cle):
        return next(e for e in rapport["etapes"] if e["cle"] == cle)

    def test_chaque_etape_compte_les_eleves_une_seule_fois(self):
        a = self.eleve("677100001", cursus=self.cursus)
        self.eleve("677100002")
        self.seance(a, termine=True, ordre=1)
        self.seance(a, termine=True, jours_apres_inscription=1, ordre=1)
        rapport = entonnoir(30, maintenant=self.maintenant)

        self.assertEqual(self.etape(rapport, "inscrits")["eleves"], 2)
        self.assertEqual(self.etape(rapport, "examen_declare")["eleves"], 1)
        self.assertEqual(self.etape(rapport, "seance_terminee")["eleves"], 1)
        self.assertEqual(self.etape(rapport, "examen_declare")["part_des_inscrits"], 50.0)

    def test_une_seance_seulement_proposee_n_est_pas_terminee(self):
        a = self.eleve("677100003", cursus=self.cursus)
        self.seance(a, termine=False)
        rapport = entonnoir(30, maintenant=self.maintenant)

        self.assertEqual(self.etape(rapport, "seance_lancee")["eleves"], 1)
        self.assertEqual(self.etape(rapport, "seance_terminee")["eleves"], 0)

    def test_le_personnel_et_les_comptes_hors_fenetre_sont_exclus(self):
        self.eleve("677100004", is_staff=True)
        self.eleve("677100005", jours=90)
        rapport = entonnoir(30, maintenant=self.maintenant)
        self.assertEqual(self.etape(rapport, "inscrits")["eleves"], 0)

    def test_paiement_tente_puis_reussi(self):
        a, b = self.eleve("677100006"), self.eleve("677100007")
        self.paiement(a, StatutTransaction.SUCCESSFUL)
        self.paiement(b, StatutTransaction.FAILED)
        rapport = entonnoir(30, maintenant=self.maintenant)

        self.assertEqual(self.etape(rapport, "paiement_tente")["eleves"], 2)
        self.assertEqual(self.etape(rapport, "paiement_reussi")["eleves"], 1)
        self.assertEqual(rapport["paiements"]["eleves_n_ayant_jamais_paye"], 1)
        self.assertEqual(rapport["paiements"]["reussite"], 50.0)

    def test_un_eleve_qui_a_echoue_puis_reussi_n_est_pas_un_abandon(self):
        a = self.eleve("677100008")
        self.paiement(a, StatutTransaction.FAILED)
        self.paiement(a, StatutTransaction.SUCCESSFUL)
        rapport = entonnoir(30, maintenant=self.maintenant)
        self.assertEqual(rapport["paiements"]["eleves_n_ayant_jamais_paye"], 0)

    def test_un_paiement_en_attente_depuis_peu_n_est_pas_signale(self):
        a = self.eleve("677100009")
        self.paiement(a, StatutTransaction.PENDING, age=timedelta(minutes=5))
        self.paiement(a, StatutTransaction.PENDING, age=timedelta(hours=3))
        rapport = entonnoir(30, maintenant=self.maintenant)
        self.assertEqual(rapport["paiements"]["en_attente_depuis_plus_d_une_heure"], 1)

    def test_retour_apres_sept_jours_ne_juge_que_les_comptes_assez_anciens(self):
        revenu = self.eleve("677100010", jours=20)
        self.seance(revenu, termine=True, jours_apres_inscription=1)
        self.seance(revenu, termine=True, jours_apres_inscription=10)
        parti = self.eleve("677100011", jours=20)
        self.seance(parti, termine=True, jours_apres_inscription=1)
        self.eleve("677100012", jours=2)  # trop récent pour être jugé

        retour = entonnoir(30, maintenant=self.maintenant)["retour_j7"]

        self.assertEqual(retour["eleves_assez_anciens"], 2)
        self.assertEqual(retour["revenus_apres_7_jours"], 1)
        self.assertEqual(retour["part"], 50.0)

    def test_aucune_division_par_zero_sans_inscrit(self):
        rapport = entonnoir(30, maintenant=self.maintenant)
        self.assertIsNone(self.etape(rapport, "examen_declare")["part_des_inscrits"])
        self.assertIsNone(rapport["retour_j7"]["part"])

    def test_la_commande_s_execute(self):
        sortie = StringIO()
        call_command("rapport_entonnoir", "--jours", "30", stdout=sortie)
        self.assertIn("Comptes créés", sortie.getvalue())


class EntonnoirApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_reserve_a_l_equipe(self):
        eleve = User.objects.create_user(phone_number="677100020", password="x")
        self.client.force_authenticate(user=eleve)
        self.assertEqual(self.client.get("/analytics/entonnoir/").status_code, 403)

        self.client.force_authenticate(user=None)
        self.assertIn(self.client.get("/analytics/entonnoir/").status_code, (401, 403))

    def test_l_equipe_lit_l_entonnoir(self):
        equipe = User.objects.create_user(phone_number="677100021", password="x", is_staff=True)
        self.client.force_authenticate(user=equipe)

        reponse = self.client.get("/analytics/entonnoir/?jours=7")

        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse.data["fenetre_jours"], 7)

    def test_fenetre_invalide(self):
        equipe = User.objects.create_user(phone_number="677100022", password="x", is_staff=True)
        self.client.force_authenticate(user=equipe)
        self.assertEqual(self.client.get("/analytics/entonnoir/?jours=abc").status_code, 400)
        self.assertEqual(self.client.get("/analytics/entonnoir/?jours=0").status_code, 400)
