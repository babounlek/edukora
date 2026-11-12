"""
Tarification au mois (décision du 2026-11-11) : 2 000 FCFA par mois, l'élève choisit le nombre de mois (1 à
`Plan.mois_max`, c'est-à-dire jusqu'à la fin de l'examen) et paie `mois × prix du mois`. Tout accès payé donne tout.

Ce qui doit rester vrai : le serveur recalcule TOUJOURS le montant (jamais celui du client), le nombre de mois est
borné par la fin de l'examen, le rabais du second enfant survit aux renouvellements mensuels, et la campagne s'applique
au prix du mois (donc le total vaut toujours `mois × prix du mois affiché`).
"""

import importlib
from datetime import timedelta
from unittest.mock import patch

from django.apps import apps as apps_django
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from access.services import has_access_jusqua_examen
from catalog.models import Cursus, Examen
from payments.models import (
    ManualPayment, ManualPaymentStatus, MobileMoneyAccount, MobileMoneyOperator, StatutTransaction, Transaction,
)
from users.models import Profil, User

from .models import (
    JOURS_PAR_MOIS, MOIS_MAX_SANS_SESSION, Campagne, DureeMode, InscriptionInedite, Plan, ProductType, Subscription,
    est_enfant_supplementaire,
)


def _cursus():
    return Cursus.objects.get(examen=Examen.BAC, series__code="C")


def _campagne(pourcentage=10):
    maintenant = timezone.now()
    return Campagne.objects.create(
        nom="Offre fondateurs", pourcentage=pourcentage,
        debut=maintenant - timedelta(days=1), fin=maintenant + timedelta(days=13),
    )


def _session_dans(jours):
    """Un compte à rebours d'examen qui se termine dans `jours` jours (remplace la lecture des ExamSession)."""
    fin = timezone.now().date() + timedelta(days=jours)
    return {"date_examen": fin - timedelta(days=3), "date_fin": fin}


class _Base(TestCase):
    def setUp(self):
        self.cursus = _cursus()
        self.user = User.objects.create_user(phone_number="677000601", password="x")
        self.premier = self.user.profils.first()
        self.plan = Plan.objects.create(
            name="BAC Série C - Au mois", cursus=self.cursus, price=2000, duration_mode=DureeMode.MENSUEL,
            duration_days=JOURS_PAR_MOIS,
        )

    def _abonner(self, profil, *, expire_dans=60, cree_il_y_a=0):
        sub = Subscription.objects.create(
            user=self.user, profil=profil, cursus=self.cursus,
            expires_at=timezone.now() + timedelta(days=expire_dans), duration_mode=DureeMode.MENSUEL,
        )
        if cree_il_y_a:
            Subscription.objects.filter(pk=sub.pk).update(created_at=timezone.now() - timedelta(days=cree_il_y_a))
        return sub

    def _cadet(self):
        return Profil.objects.create(compte=self.user, prenom="Cadet", ordre=1)


class PrixDuMoisTests(_Base):
    def test_le_total_est_le_prix_du_mois_fois_le_nombre_de_mois(self):
        self.assertEqual(self.plan.effective_price(), 2000)
        self.assertEqual(self.plan.effective_price(mois=1), 2000)
        self.assertEqual(self.plan.effective_price(mois=5), 10000)
        tarif = self.plan.tarif(mois=7)
        self.assertEqual((tarif.prix, tarif.reference, tarif.campagne), (14000, 14000, None))

    def test_un_plan_vendu_a_l_unite_ignore_le_nombre_de_mois(self):
        jusqua = Plan.objects.create(
            name="Ancien", cursus=self.cursus, price=15000, duration_mode=DureeMode.JUSQUA_EXAMEN,
        )
        self.assertEqual(jusqua.effective_price(mois=4), 15000)

    def test_la_duree_est_de_trente_jours_par_mois(self):
        self.assertEqual(self.plan.effective_duration_days(), 30)
        self.assertEqual(self.plan.effective_duration_days(3), 90)

    def test_la_campagne_s_applique_au_prix_du_mois_puis_se_multiplie(self):
        campagne = _campagne(10)
        un_mois = self.plan.tarif(mois=1)
        self.assertEqual((un_mois.prix, un_mois.reference, un_mois.campagne), (1800, 2000, campagne))
        trois_mois = self.plan.tarif(mois=3)
        # 3 × 1 800 : exactement le prix du mois affiché, multiplié - aucun écart d'arrondi.
        self.assertEqual((trois_mois.prix, trois_mois.reference), (5400, 6000))

    def test_l_enfant_supplementaire_paie_1600_le_mois(self):
        self._abonner(self.premier)
        cadet = self._cadet()
        self.assertEqual(self.plan.prix_enfant_supplementaire(), 1600)
        self.assertEqual(self.plan.effective_price(self.user, cadet, mois=3), 4800)
        # Le premier enfant, lui, garde le tarif de référence à chaque renouvellement.
        self.assertEqual(self.plan.effective_price(self.user, self.premier, mois=3), 6000)

    def test_remise_famille_et_campagne_se_cumulent_au_mois(self):
        self._abonner(self.premier)
        cadet = self._cadet()
        _campagne(10)
        self.assertEqual(self.plan.effective_price(self.user, cadet), 1440)  # 1 600 × 0,9
        self.assertEqual(self.plan.effective_price(self.user, cadet, mois=2), 2880)


class EnfantSupplementaireTests(_Base):
    def test_le_rabais_du_second_enfant_survit_a_son_renouvellement(self):
        """Au mois, on renouvelle souvent : le second ne doit pas retomber à 2 000 dès son deuxième achat."""
        self._abonner(self.premier, cree_il_y_a=40)
        cadet = self._cadet()
        self._abonner(cadet, cree_il_y_a=10)
        self.assertTrue(est_enfant_supplementaire(self.user, cadet))
        self.assertFalse(est_enfant_supplementaire(self.user, self.premier))

    def test_le_premier_enfant_n_est_jamais_supplementaire_meme_quand_le_cadet_est_actif(self):
        cadet = self._cadet()
        self._abonner(cadet, cree_il_y_a=5)
        self._abonner(self.premier, cree_il_y_a=50)
        self.assertFalse(est_enfant_supplementaire(self.user, self.premier))

    def test_l_ancien_accès_expire_depuis_longtemps_ne_compte_plus(self):
        self._abonner(self.premier, expire_dans=-120, cree_il_y_a=300)
        cadet = self._cadet()
        self.assertFalse(est_enfant_supplementaire(self.user, cadet))

    def test_un_accès_expire_depuis_peu_compte_encore(self):
        self._abonner(self.premier, expire_dans=-20, cree_il_y_a=100)
        cadet = self._cadet()
        self.assertTrue(est_enfant_supplementaire(self.user, cadet))

    def test_un_visiteur_ou_une_famille_sans_acces_paie_le_tarif_de_reference(self):
        self.assertFalse(est_enfant_supplementaire(None))
        self.assertFalse(est_enfant_supplementaire(self.user, self.premier))


class MoisMaxTests(_Base):
    def test_c_est_le_nombre_de_mois_jusqu_a_la_fin_de_l_examen_arrondi_au_superieur(self):
        with patch("subscriptions.models.ExamSession.compte_a_rebours_pour", return_value=_session_dans(100)):
            self.assertEqual(self.plan.mois_max(), 4)  # 100 jours = 3,3 mois -> 4
        with patch("subscriptions.models.ExamSession.compte_a_rebours_pour", return_value=_session_dans(90)):
            self.assertEqual(self.plan.mois_max(), 3)  # pile 3 mois
        with patch("subscriptions.models.ExamSession.compte_a_rebours_pour", return_value=_session_dans(205)):
            self.assertEqual(self.plan.mois_max(), 7)

    def test_il_en_reste_toujours_au_moins_un(self):
        with patch("subscriptions.models.ExamSession.compte_a_rebours_pour", return_value=_session_dans(2)):
            self.assertEqual(self.plan.mois_max(), 1)
        with patch("subscriptions.models.ExamSession.compte_a_rebours_pour", return_value=_session_dans(-10)):
            self.assertEqual(self.plan.mois_max(), 1)

    def test_sans_session_connue_on_retombe_sur_une_annee_scolaire(self):
        with patch("subscriptions.models.ExamSession.compte_a_rebours_pour", return_value=None):
            self.assertEqual(self.plan.mois_max(), MOIS_MAX_SANS_SESSION)

    def test_un_plan_qui_ne_se_vend_pas_au_mois_s_achete_en_une_fois(self):
        fixe = Plan.objects.create(name="Fixe", cursus=self.cursus, price=3000, duration_days=30)
        self.assertEqual(fixe.mois_max(), 1)
        self.assertTrue(fixe.mois_valide(1))
        self.assertFalse(fixe.mois_valide(2))

    def test_mois_valide_refuse_tout_ce_qui_n_est_pas_un_nombre_dans_la_plage(self):
        with patch("subscriptions.models.ExamSession.compte_a_rebours_pour", return_value=_session_dans(100)):
            self.assertTrue(self.plan.mois_valide(1))
            self.assertTrue(self.plan.mois_valide(4))
            for mauvais in (0, -1, 5, True, "3", None, 2.5):
                self.assertFalse(self.plan.mois_valide(mauvais), mauvais)

    def test_l_api_expose_mois_max_et_le_prix_d_un_mois(self):
        with patch("subscriptions.models.ExamSession.compte_a_rebours_pour", return_value=_session_dans(100)):
            ligne = next(
                p for p in self.client.get("/subscriptions/plans/", {"cursus": self.cursus.id}).json()
                if p["id"] == self.plan.id
            )
        self.assertEqual(ligne["mois_max"], 4)
        self.assertEqual(ligne["effective_price"], 2000)
        self.assertEqual(ligne["effective_duration_days"], 30)
        self.assertEqual(ligne["duration_mode"], "MENSUEL")
        self.assertTrue(ligne["inclut_inedit"])

    def test_un_plan_au_mois_inclut_toujours_les_inedites(self):
        plan = Plan.objects.create(
            name="x", cursus=self.cursus, price=2000, duration_mode=DureeMode.MENSUEL, inclut_inedit=False,
        )
        self.assertTrue(plan.inclut_inedit)


@override_settings(CAMPAY_ACTIVE=True)
class AchatAuMoisTests(_Base):
    def setUp(self):
        super().setUp()
        MobileMoneyAccount.objects.create(operator=MobileMoneyOperator.ORANGE, phone_number="677000099", account_name="Edukora")
        self.api = APIClient()
        self.api.force_authenticate(user=self.user)
        self.patch_session = patch(
            "subscriptions.models.ExamSession.compte_a_rebours_pour", return_value=_session_dans(100),
        )
        self.patch_session.start()
        self.addCleanup(self.patch_session.stop)

    def _initier(self, **surcharges):
        donnees = {"plan_id": self.plan.id, "phone_number": self.user.phone_number}
        donnees.update(surcharges)
        with patch("payments.campay_client.init_collect", return_value={"reference": "ref-1", "status": "PENDING"}):
            return self.api.post("/payments/initiate/", donnees)

    def test_campay_facture_le_nombre_de_mois_choisi(self):
        reponse = self._initier(mois=3)
        self.assertEqual(reponse.status_code, 200)
        transaction = Transaction.objects.get(pk=reponse.data["transaction_id"])
        self.assertEqual((transaction.mois, transaction.amount), (3, 6000))

    def test_sans_mois_on_achete_un_seul_mois(self):
        transaction = Transaction.objects.get(pk=self._initier().data["transaction_id"])
        self.assertEqual((transaction.mois, transaction.amount), (1, 2000))

    def test_le_nombre_de_mois_est_borne_par_la_fin_de_l_examen(self):
        reponse = self._initier(mois=5)  # mois_max = 4
        self.assertEqual(reponse.status_code, 400)
        self.assertEqual(reponse.data["mois_max"], 4)
        self.assertFalse(Transaction.objects.exists())

    def test_un_nombre_de_mois_invalide_est_refuse_sans_creer_de_transaction(self):
        for mauvais in (0, -2, "abc", 2.5):
            self.assertEqual(self._initier(mois=mauvais).status_code, 400, mauvais)
        self.assertFalse(Transaction.objects.exists())

    def test_le_paiement_confirme_ouvre_trente_jours_par_mois_et_les_inedites(self):
        reponse = self._initier(mois=3)
        transaction = Transaction.objects.get(pk=reponse.data["transaction_id"])
        transaction.status = StatutTransaction.SUCCESSFUL
        transaction.save()
        transaction._confirmer_succes()
        sub = Subscription.objects.get(user=self.user, cursus=self.cursus)
        self.assertEqual(sub.duration_mode, DureeMode.MENSUEL)
        reste = (sub.expires_at - timezone.now()).total_seconds() / 86400
        self.assertAlmostEqual(reste, 90, delta=0.1)
        inedite = InscriptionInedite.objects.get(user=self.user, cursus=self.cursus)
        self.assertAlmostEqual((inedite.expires_at - timezone.now()).total_seconds() / 86400, 90, delta=0.1)

    def test_un_deuxieme_achat_s_ajoute_a_la_suite_de_l_acces_en_cours(self):
        for mois in (2, 1):
            transaction = Transaction.objects.get(pk=self._initier(mois=mois).data["transaction_id"])
            transaction.status = StatutTransaction.SUCCESSFUL
            transaction.save()
            transaction._confirmer_succes()
        sub = Subscription.objects.get(user=self.user, cursus=self.cursus)
        self.assertAlmostEqual((sub.expires_at - timezone.now()).total_seconds() / 86400, 90, delta=0.1)

    def test_tout_acces_au_mois_donne_les_fonctions_de_la_formule_complete(self):
        self.assertFalse(has_access_jusqua_examen(self.user, self.cursus))
        self._abonner(self.premier)
        self.assertTrue(has_access_jusqua_examen(self.user, self.cursus))

    # --- paiement manuel -------------------------------------------------------------------------

    def _declarer(self, **surcharges):
        donnees = {
            "plan": self.plan.id, "operator": MobileMoneyOperator.ORANGE,
            "payer_phone_number": self.user.phone_number, "transaction_reference": "OM-MOIS-1",
        }
        donnees.update(surcharges)
        with patch("payments.models._notifier_utilisateur"):
            return self.api.post("/payments/manual/declare/", donnees)

    def test_le_paiement_manuel_attend_le_total_des_mois_choisis(self):
        reponse = self._declarer(mois=3)
        self.assertEqual(reponse.status_code, 201, reponse.data)
        paiement = ManualPayment.objects.get()
        self.assertEqual((paiement.mois, paiement.amount_expected, paiement.amount_declared), (3, 6000, 6000))

    def test_un_montant_declare_inferieur_au_total_est_refuse(self):
        reponse = self._declarer(mois=3, amount_declared=2000)
        self.assertEqual(reponse.status_code, 400)
        self.assertIn("amount_declared", reponse.data)

    def test_le_paiement_manuel_refuse_trop_de_mois(self):
        reponse = self._declarer(mois=5)
        self.assertEqual(reponse.status_code, 400)
        self.assertIn("mois", reponse.data)
        self.assertFalse(ManualPayment.objects.exists())

    def test_la_validation_admin_ouvre_les_mois_declares(self):
        self._declarer(mois=2)
        paiement = ManualPayment.objects.get()
        admin = User.objects.create_user(phone_number="677000699", password="x", is_staff=True)
        with patch("payments.models._notifier_utilisateur"):
            paiement.approve(admin)
        paiement.refresh_from_db()
        self.assertEqual(paiement.status, ManualPaymentStatus.APPROVED)
        sub = Subscription.objects.get(user=self.user, cursus=self.cursus)
        self.assertAlmostEqual((sub.expires_at - timezone.now()).total_seconds() / 86400, 60, delta=0.1)


class MigrationPlansAuMoisTests(TestCase):
    """0027 : un plan au mois par cursus qui avait un plan Jusqu'à l'Examen actif, et celui-ci est désactivé."""

    def setUp(self):
        self.migration = importlib.import_module("subscriptions.migrations.0027_plans_au_mois")
        self.cursus = _cursus()
        Plan.objects.filter(cursus=self.cursus).delete()
        self.jusqua = Plan.objects.create(
            name="BAC Série C - Jusqu'à l'Examen", cursus=self.cursus, price=15000,
            duration_mode=DureeMode.JUSQUA_EXAMEN,
        )

    def test_cree_le_plan_au_mois_et_desactive_l_ancien(self):
        self.migration.appliquer(apps_django, None)
        mensuel = Plan.objects.get(cursus=self.cursus, duration_mode=DureeMode.MENSUEL)
        self.assertEqual((mensuel.price, mensuel.duration_days, mensuel.is_active), (2000, 30, True))
        self.assertEqual(mensuel.name, "BAC Série C - Au mois")
        self.assertEqual(mensuel.product_type, ProductType.ABONNEMENT)
        self.assertTrue(mensuel.inclut_inedit)
        self.jusqua.refresh_from_db()
        self.assertFalse(self.jusqua.is_active)

    def test_rejouee_elle_ne_cree_rien_de_plus(self):
        self.migration.appliquer(apps_django, None)
        self.migration.appliquer(apps_django, None)
        self.assertEqual(Plan.objects.filter(cursus=self.cursus, duration_mode=DureeMode.MENSUEL).count(), 1)

    def test_l_ancien_mensuel_a_duree_fixe_reste_inactif(self):
        ancien = Plan.objects.create(
            name="BAC Série C - Mensuel (30 jours)", cursus=self.cursus, price=2000, duration_days=30, is_active=False,
        )
        self.migration.appliquer(apps_django, None)
        ancien.refresh_from_db()
        self.assertFalse(ancien.is_active)

    def test_annuler_remet_en_vente_l_ancienne_formule(self):
        self.migration.appliquer(apps_django, None)
        self.migration.annuler(apps_django, None)
        self.jusqua.refresh_from_db()
        self.assertTrue(self.jusqua.is_active)
        self.assertFalse(Plan.objects.get(cursus=self.cursus, duration_mode=DureeMode.MENSUEL).is_active)
