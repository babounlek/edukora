"""
Campagne promotionnelle (« Offre fondateurs » -20 %, etc.) : le prix doit baisser partout où il est
lu (catalogue, paiement Campay, déclaration manuelle), jamais se cumuler avec la remise famille,
et chaque paiement doit garder sa campagne pour qu'on puisse mesurer ce qu'elle a rapporté.
"""

from datetime import timedelta
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from analytics.funnel import rapport_campagnes
from catalog.models import Cursus, Examen
from payments.models import ManualPayment, MobileMoneyAccount, MobileMoneyOperator, Transaction
from revendeurs.models import AttributionRevendeur, Commission, Revendeur, StatutRevendeur, TypeRevendeur
from users.models import Profil, User

from .models import Campagne, DureeMode, Plan, ProductType, Subscription


def _cursus():
    return Cursus.objects.get(examen=Examen.BAC, series__code="C")


def _campagne(pourcentage=20, *, debut=None, fin=None, **extra):
    maintenant = timezone.now()
    return Campagne.objects.create(
        nom="Offre fondateurs", pourcentage=pourcentage,
        debut=debut or maintenant - timedelta(days=1), fin=fin or maintenant + timedelta(days=13), **extra,
    )


class _Base(TestCase):
    def setUp(self):
        self.cursus = _cursus()
        self.user = User.objects.create_user(phone_number="677000501", password="x")
        self.plan = Plan.objects.create(
            name="Jusqu'à l'Examen", cursus=self.cursus, price=15000, duration_mode=DureeMode.JUSQUA_EXAMEN,
        )

    def _deuxieme_enfant(self):
        Subscription.objects.create(
            user=self.user, profil=self.user.profils.first(), cursus=self.cursus,
            expires_at=timezone.now() + timedelta(days=200), duration_mode=DureeMode.JUSQUA_EXAMEN,
        )
        return Profil.objects.create(compte=self.user, prenom="Cadet", ordre=1)


class TarifTests(_Base):
    def test_sans_campagne_le_prix_ne_change_pas(self):
        tarif = self.plan.tarif()
        self.assertEqual((tarif.prix, tarif.reference, tarif.campagne), (15000, 15000, None))

    def test_une_campagne_ouverte_baisse_le_prix_et_garde_la_reference(self):
        campagne = _campagne(20)
        tarif = self.plan.tarif()
        self.assertEqual((tarif.prix, tarif.reference, tarif.campagne), (12000, 15000, campagne))
        self.assertEqual(self.plan.effective_price(), 12000)

    def test_remise_de_10_pour_cent(self):
        _campagne(10)
        self.assertEqual(self.plan.effective_price(), 13500)

    def test_campagne_suspendue_a_venir_ou_terminee_ne_change_rien(self):
        maintenant = timezone.now()
        _campagne(active=False)
        _campagne(debut=maintenant + timedelta(days=2), fin=maintenant + timedelta(days=9))
        _campagne(debut=maintenant - timedelta(days=9), fin=maintenant - timedelta(days=2))
        self.assertEqual(self.plan.effective_price(), 15000)

    def test_la_remise_famille_et_la_campagne_ne_se_cumulent_jamais(self):
        cadet = self._deuxieme_enfant()
        # -20 % de campagne = 12 000 = déjà le tarif du 2e enfant : la campagne ne fait rien baisser.
        _campagne(20)
        tarif = self.plan.tarif(user=self.user, profil=cadet)
        self.assertEqual((tarif.prix, tarif.reference, tarif.campagne), (12000, 12000, None))

    def test_une_campagne_plus_forte_que_la_remise_famille_l_emporte(self):
        cadet = self._deuxieme_enfant()
        campagne = _campagne(30)
        tarif = self.plan.tarif(user=self.user, profil=cadet)
        # 30 % sur le tarif de référence (15 000) = 10 500, jamais 30 % de 12 000.
        self.assertEqual((tarif.prix, tarif.reference, tarif.campagne), (10500, 12000, campagne))

    def test_un_plan_hors_jusqua_examen_n_est_pas_remise(self):
        _campagne(20)
        mensuel = Plan.objects.create(name="Mensuel", cursus=self.cursus, price=1000, duration_days=30)
        self.assertEqual(mensuel.effective_price(), 1000)

    def test_campagne_limitee_a_certains_cursus(self):
        campagne = _campagne(20)
        autre = Cursus.objects.exclude(pk=self.cursus.pk).first()
        campagne.cursus.add(autre)
        self.assertEqual(self.plan.effective_price(), 15000)
        campagne.cursus.add(self.cursus)
        self.assertEqual(self.plan.effective_price(), 12000)


class ValidationTests(_Base):
    def test_deux_campagnes_actives_ne_peuvent_pas_se_chevaucher(self):
        _campagne()
        maintenant = timezone.now()
        autre = Campagne(nom="Autre", pourcentage=10, debut=maintenant + timedelta(days=5), fin=maintenant + timedelta(days=20))
        with self.assertRaises(ValidationError):
            autre.full_clean()

    def test_une_campagne_suspendue_ne_bloque_pas_la_suivante(self):
        _campagne(active=False)
        maintenant = timezone.now()
        Campagne(nom="Autre", pourcentage=10, debut=maintenant, fin=maintenant + timedelta(days=7)).full_clean()

    def test_modifier_une_campagne_ne_la_met_pas_en_conflit_avec_elle_meme(self):
        _campagne().full_clean()

    def test_fin_avant_debut_et_remise_excessive_refusees(self):
        maintenant = timezone.now()
        with self.assertRaises(ValidationError):
            Campagne(nom="x", pourcentage=20, debut=maintenant, fin=maintenant - timedelta(days=1)).full_clean()
        with self.assertRaises(ValidationError):
            Campagne(nom="x", pourcentage=51, debut=maintenant, fin=maintenant + timedelta(days=1)).full_clean()
        with self.assertRaises(ValidationError):
            Campagne(nom="x", pourcentage=0, debut=maintenant, fin=maintenant + timedelta(days=1)).full_clean()


class DelaiDeGraceTests(_Base):
    def test_juste_apres_la_fin_une_declaration_garde_le_prix_de_campagne(self):
        maintenant = timezone.now()
        campagne = _campagne(fin=maintenant - timedelta(hours=3))
        self.assertIsNone(Campagne.objects.en_cours())
        self.assertEqual(Campagne.objects.pour_declaration(), campagne)

    def test_passe_le_delai_de_grace_plus_de_campagne(self):
        _campagne(fin=timezone.now() - timedelta(hours=49))
        self.assertIsNone(Campagne.objects.pour_declaration())

    def test_un_paiement_date_apres_la_fin_n_a_pas_droit_a_la_campagne(self):
        maintenant = timezone.now()
        _campagne(fin=maintenant - timedelta(hours=3))
        self.assertIsNone(Campagne.objects.pour_declaration(paid_at=maintenant - timedelta(hours=1)))

    def test_un_paiement_date_avant_la_fin_y_a_droit(self):
        maintenant = timezone.now()
        campagne = _campagne(fin=maintenant - timedelta(hours=3))
        self.assertEqual(Campagne.objects.pour_declaration(paid_at=maintenant - timedelta(hours=5)), campagne)


class CatalogueApiTests(_Base):
    def test_les_plans_exposent_le_prix_barre_et_la_campagne(self):
        campagne = _campagne(20)
        ligne = next(
            p for p in self.client.get(reverse("subscriptions:plan-list"), {"cursus": self.cursus.id}).json()
            if p["id"] == self.plan.id
        )
        self.assertEqual(ligne["effective_price"], 12000)
        self.assertEqual(ligne["prix_reference"], 15000)
        self.assertEqual(ligne["price"], 15000)
        self.assertEqual(ligne["campagne"]["id"], campagne.id)
        self.assertEqual(ligne["campagne"]["pourcentage"], 20)

    def test_sans_campagne_pas_de_prix_barre(self):
        ligne = next(
            p for p in self.client.get(reverse("subscriptions:plan-list"), {"cursus": self.cursus.id}).json()
            if p["id"] == self.plan.id
        )
        self.assertEqual((ligne["effective_price"], ligne["prix_reference"], ligne["campagne"]), (15000, 15000, None))

    def test_endpoint_de_la_campagne_en_cours(self):
        self.assertIsNone(self.client.get(reverse("subscriptions:campagne-en-cours")).json()["campagne"])
        _campagne(20)
        campagne = self.client.get(reverse("subscriptions:campagne-en-cours")).json()["campagne"]
        self.assertEqual(campagne["nom"], "Offre fondateurs")
        self.assertEqual((campagne["prix"], campagne["prix_reference"], campagne["prix_enfant_supplementaire"]), (12000, 15000, 12000))


@override_settings(CAMPAY_ACTIVE=True)
class PaiementTests(_Base):
    def setUp(self):
        super().setUp()
        MobileMoneyAccount.objects.create(operator=MobileMoneyOperator.ORANGE, phone_number="677000099", account_name="Edukora")
        self.api = APIClient()
        self.api.force_authenticate(user=self.user)

    def _declarer(self, **surcharges):
        donnees = {
            "plan": self.plan.id, "operator": MobileMoneyOperator.ORANGE, "payer_phone_number": self.user.phone_number,
            "transaction_reference": "OM-CAMP-1",
        }
        donnees.update(surcharges)
        return self.api.post("/payments/manual/declare/", donnees)

    @patch("payments.campay_client.init_collect")
    def test_le_paiement_campay_facture_le_prix_de_campagne_et_garde_la_campagne(self, mock_init):
        mock_init.return_value = {"reference": "campay-ref-camp", "status": "PENDING"}
        campagne = _campagne(20)
        reponse = self.api.post("/payments/initiate/", {"plan_id": self.plan.id, "phone_number": self.user.phone_number})
        self.assertEqual(reponse.status_code, 200, reponse.content)
        transaction = Transaction.objects.get(pk=reponse.data["transaction_id"])
        self.assertEqual(transaction.amount, 12000)
        self.assertEqual(transaction.campagne, campagne)

    @patch("payments.campay_client.init_collect")
    def test_hors_campagne_le_paiement_campay_n_a_pas_de_campagne(self, mock_init):
        mock_init.return_value = {"reference": "campay-ref-plein", "status": "PENDING"}
        reponse = self.api.post("/payments/initiate/", {"plan_id": self.plan.id, "phone_number": self.user.phone_number})
        transaction = Transaction.objects.get(pk=reponse.data["transaction_id"])
        self.assertEqual((transaction.amount, transaction.campagne), (15000, None))

    def test_declaration_manuelle_attend_le_prix_de_campagne(self):
        campagne = _campagne(20)
        reponse = self._declarer()
        self.assertEqual(reponse.status_code, 201, reponse.content)
        paiement = ManualPayment.objects.get(pk=reponse.data["id"])
        self.assertEqual((paiement.amount_expected, paiement.amount_declared, paiement.campagne), (12000, 12000, campagne))

    def test_declarer_le_prix_plein_pendant_la_campagne_reste_accepte(self):
        _campagne(20)
        paiement = ManualPayment.objects.get(pk=self._declarer(amount_declared=15000).data["id"])
        self.assertEqual((paiement.amount_expected, paiement.amount_declared), (12000, 15000))

    def test_declaration_juste_apres_la_fin_accepte_le_prix_de_campagne(self):
        campagne = _campagne(fin=timezone.now() - timedelta(hours=5))
        reponse = self._declarer(amount_declared=12000)
        self.assertEqual(reponse.status_code, 201, reponse.content)
        self.assertEqual(ManualPayment.objects.get(pk=reponse.data["id"]).campagne, campagne)

    def test_declaration_longtemps_apres_la_fin_exige_le_prix_plein(self):
        _campagne(fin=timezone.now() - timedelta(days=5))
        self.assertEqual(self._declarer(amount_declared=12000).status_code, 400)

    def test_declaration_d_un_paiement_date_apres_la_fin_exige_le_prix_plein(self):
        maintenant = timezone.now()
        _campagne(fin=maintenant - timedelta(hours=5))
        reponse = self._declarer(amount_declared=12000, paid_at=(maintenant - timedelta(hours=1)).isoformat())
        self.assertEqual(reponse.status_code, 400)

    def test_la_commission_revendeur_porte_sur_le_prix_paye(self):
        _campagne(20)
        revendeur = Revendeur.objects.create(
            user=User.objects.create_user(phone_number="677900001", password="x"), nom_affiche="Revendeur", code="DEMO42",
            type=TypeRevendeur.REPETITEUR, statut=StatutRevendeur.ACTIF,
        )
        AttributionRevendeur.objects.create(client=self.user, revendeur=revendeur)
        admin = User.objects.create_user(phone_number="677900099", password="x", is_staff=True)
        paiement = ManualPayment.objects.get(pk=self._declarer(payer_phone_number="690000001").data["id"])

        with patch("users.sms_backends.get_sms_backend"):
            paiement.approve(admin)

        commission = Commission.objects.get(manual_payment=paiement)
        self.assertEqual((commission.base_fcfa, commission.montant_fcfa), (12000, 1680))


class RapportCampagnesTests(_Base):
    def test_le_rapport_compare_la_campagne_a_la_periode_d_avant(self):
        maintenant = timezone.now()
        campagne = _campagne(20, debut=maintenant - timedelta(days=10), fin=maintenant + timedelta(days=4))
        Transaction.objects.create(
            user=self.user, profil=self.user.profils.first(), plan=self.plan, amount=12000, phone_number="677000501",
            status="SUCCESSFUL", campagne=campagne,
        )

        (ligne,) = rapport_campagnes(timezone.now())

        self.assertEqual(ligne["nom"], "Offre fondateurs")
        self.assertTrue(ligne["en_cours"])
        self.assertEqual(ligne["jours_mesures"], 10.0)
        self.assertEqual(ligne["pendant"]["paiements_valides"], 1)
        self.assertEqual(ligne["pendant"]["paiements_au_prix_de_campagne"], 1)
        self.assertEqual(ligne["pendant"]["chiffre_affaires"], 12000)
        self.assertEqual(ligne["pendant"]["comptes_crees"], 1)
        self.assertEqual(ligne["pendant"]["taux_conversion"], 100.0)
        self.assertEqual(ligne["juste_avant"]["paiements_valides"], 0)

    def test_une_campagne_a_venir_n_apparait_pas(self):
        maintenant = timezone.now()
        _campagne(debut=maintenant + timedelta(days=2), fin=maintenant + timedelta(days=9))
        self.assertEqual(rapport_campagnes(maintenant), [])
