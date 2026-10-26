from datetime import timedelta
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Cursus, Examen
from payments.models import ManualPayment, MobileMoneyOperator, StatutTransaction, Transaction
from subscriptions.models import Plan, Subscription
from users.email_service import request_email_code, verify_email_code
from users.google import resolve_google_account
from users.models import CodeCanal, OTPCode, User
from users.otp_service import verify_otp
from users.phone import to_e164

from .models import (
    AttributionRevendeur,
    Commission,
    CommissionDejaAcquise,
    Revendeur,
    SourceAttribution,
    StatutCommission,
    StatutRevendeur,
    TypeRevendeur,
)
from .services import (
    enregistrer_commission,
    enregistrer_commission_securise,
    masquer_client,
    rattacher_tardivement,
)


def _cursus():
    return Cursus.objects.get(examen=Examen.BAC, series__code="C")


def _revendeur(tel="677900001", code="DEMO42", type=TypeRevendeur.REPETITEUR, statut=StatutRevendeur.ACTIF, **extra):
    user = User.objects.create_user(phone_number=tel, password="x")
    return Revendeur.objects.create(user=user, nom_affiche=f"Revendeur {code}", code=code, type=type, statut=statut, **extra)


class _Base(TestCase):
    def setUp(self):
        self.cursus = _cursus()
        self.admin = User.objects.create_user(phone_number="677900099", password="x", is_staff=True)
        self.plan = Plan.objects.create(name="Jusqu'à l'examen", cursus=self.cursus, price=15000, duration_days=365)
        self.revendeur = _revendeur()

    def _client(self, tel="677900010", attribue=True, **attr):
        client = User.objects.create_user(phone_number=tel, password="x")
        if attribue:
            AttributionRevendeur.objects.create(client=client, revendeur=self.revendeur, **attr)
        return client

    def _manuel(self, client, ref, montant=None, payeur=None, plan=None):
        plan = plan or self.plan
        montant = plan.price if montant is None else montant
        return ManualPayment.objects.create(
            user=client, profil=client.profils.first(), plan=plan, operator=MobileMoneyOperator.ORANGE,
            amount_expected=plan.price, amount_declared=montant,
            payer_phone_number=payeur or "699000111", transaction_reference=ref,
        )

    def _campay(self, client, montant=None, plan=None):
        plan = plan or self.plan
        return Transaction.objects.create(
            user=client, profil=client.profils.first(), plan=plan,
            amount=plan.price if montant is None else montant, phone_number="699000222",
            provider_reference=f"campay-{client.pk}-{Transaction.objects.count()}",
            status=StatutTransaction.SUCCESSFUL,
        )


class RevendeurModelTests(_Base):
    def test_code_mis_en_majuscules_et_valide(self):
        r = _revendeur(tel="677900002", code="abc123")
        self.assertEqual(r.code, "ABC123")

    def test_code_trop_court_refuse(self):
        user = User.objects.create_user(phone_number="677900003", password="x")
        with self.assertRaises(ValidationError):
            Revendeur.objects.create(user=user, nom_affiche="X", code="AB", type=TypeRevendeur.REPETITEUR)

    def test_code_egal_a_un_code_de_parrainage_refuse(self):
        autre = User.objects.create_user(phone_number="677900004", password="x")
        user = User.objects.create_user(phone_number="677900005", password="x")
        with self.assertRaises(ValidationError):
            Revendeur.objects.create(
                user=user, nom_affiche="X", code=autre.referral_code, type=TypeRevendeur.REPETITEUR,
            )

    def test_un_code_de_parrainage_genere_evite_les_codes_revendeur(self):
        # Force le premier tirage à tomber sur le code du revendeur, le second sur un code libre.
        with patch("users.models._generate_referral_code", side_effect=[self.revendeur.code, "LIBRE9"]):
            user = User.objects.create_user(phone_number="677900006", password="x")
        self.assertEqual(user.referral_code, "LIBRE9")

    def test_palier_par_defaut_pour_un_commercial_seulement(self):
        commercial = _revendeur(tel="677900007", code="COMM01", type=TypeRevendeur.COMMERCIAL)
        ecole = _revendeur(tel="677900008", code="ECOLE1", type=TypeRevendeur.ECOLE_CENTRE)
        self.assertEqual((commercial.palier_seuil, commercial.palier_taux_pct), (30, 17))
        self.assertIsNone(ecole.palier_seuil)

    def test_palier_refuse_pour_un_non_commercial(self):
        user = User.objects.create_user(phone_number="677900009", password="x")
        with self.assertRaises(ValidationError):
            Revendeur.objects.create(
                user=user, nom_affiche="X", code="REPET9", type=TypeRevendeur.REPETITEUR,
                palier_seuil=30, palier_taux_pct=17,
            )


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class AttributionALInscriptionTests(_Base):
    def test_inscription_par_telephone(self):
        OTPCode.objects.create(
            destination=to_e164("677900020"), code="111111", expires_at=timezone.now() + timedelta(minutes=5),
        )
        user = verify_otp("677900020", "111111", referral_code="demo42")

        attribution = AttributionRevendeur.objects.get(client=user)
        self.assertEqual(attribution.revendeur, self.revendeur)
        self.assertEqual(attribution.source, SourceAttribution.INSCRIPTION)
        self.assertIsNone(user.referred_by)

    def test_inscription_par_email(self):
        request_email_code("eleve@example.com")
        code = OTPCode.objects.filter(canal=CodeCanal.EMAIL, destination="eleve@example.com").latest("created_at").code
        user, cree = verify_email_code("eleve@example.com", code, referral_code=self.revendeur.code)

        self.assertTrue(cree)
        self.assertEqual(AttributionRevendeur.objects.get(client=user).revendeur, self.revendeur)

    def test_inscription_par_google(self):
        claims = {"sub": "g-rev-1", "email": "eleve@gmail.com", "email_verified": True, "name": "Awa"}
        user, cree = resolve_google_account(claims, referral_code=self.revendeur.code)

        self.assertTrue(cree)
        self.assertEqual(AttributionRevendeur.objects.get(client=user).revendeur, self.revendeur)

    def test_code_de_parrainage_ordinaire_ne_cree_pas_d_attribution(self):
        parrain = User.objects.create_user(phone_number="677900021", password="x")
        OTPCode.objects.create(
            destination=to_e164("677900022"), code="222222", expires_at=timezone.now() + timedelta(minutes=5),
        )
        user = verify_otp("677900022", "222222", referral_code=parrain.referral_code)

        self.assertEqual(user.referred_by, parrain)
        self.assertFalse(AttributionRevendeur.objects.filter(client=user).exists())

    def test_code_de_revendeur_suspendu_ou_en_attente_ignore(self):
        for i, statut in enumerate((StatutRevendeur.SUSPENDU, StatutRevendeur.EN_ATTENTE, StatutRevendeur.RESILIE)):
            Revendeur.objects.filter(pk=self.revendeur.pk).update(statut=statut)
            tel = f"67790003{i}"
            OTPCode.objects.create(
                destination=to_e164(tel), code="333333", expires_at=timezone.now() + timedelta(minutes=5),
            )
            user = verify_otp(tel, "333333", referral_code=self.revendeur.code)
            self.assertFalse(AttributionRevendeur.objects.filter(client=user).exists(), statut)

    def test_un_compte_existant_qui_se_reconnecte_n_est_pas_attribue(self):
        existant = User.objects.create_user(phone_number="677900040", password="x")
        OTPCode.objects.create(
            destination=to_e164("677900040"), code="444444", expires_at=timezone.now() + timedelta(minutes=5),
        )
        verify_otp("677900040", "444444", referral_code=self.revendeur.code)

        self.assertFalse(AttributionRevendeur.objects.filter(client=existant).exists())

    def test_le_revendeur_ne_peut_pas_s_attribuer_son_propre_numero(self):
        from .services import attribuer_a_l_inscription

        self.assertIsNone(attribuer_a_l_inscription(self.revendeur.user, self.revendeur.code))


class RattachementTardifTests(_Base):
    def test_avant_le_premier_paiement(self):
        client = self._client(attribue=False)
        attribution = rattacher_tardivement(client, self.revendeur.code)

        self.assertEqual(attribution.source, SourceAttribution.PAIEMENT)

    def test_refuse_si_deja_attribue(self):
        client = self._client()
        autre = _revendeur(tel="677900050", code="AUTRE1")

        self.assertIsNone(rattacher_tardivement(client, autre.code))
        self.assertEqual(client.attribution_revendeur.revendeur, self.revendeur)

    def test_refuse_apres_un_paiement_valide(self):
        client = self._client(attribue=False)
        self._manuel(client, "REF-TARDIF-1").approve(self.admin)

        self.assertIsNone(rattacher_tardivement(client, self.revendeur.code))

    def test_refuse_apres_un_paiement_campay_reussi(self):
        client = self._client(attribue=False)
        self._campay(client)

        self.assertIsNone(rattacher_tardivement(client, self.revendeur.code))


class CommissionCalculTests(_Base):
    def test_paiement_manuel_approuve_cree_la_commission_14_pour_cent(self):
        client = self._client()
        paiement = self._manuel(client, "REF-1")

        paiement.approve(self.admin)

        commission = Commission.objects.get(manual_payment=paiement)
        self.assertEqual((commission.base_fcfa, commission.taux_pct, commission.montant_fcfa), (15000, 14, 2100))
        self.assertEqual(commission.statut, StatutCommission.ACTIVE)
        self.assertEqual(commission.etat, "EN_ATTENTE")
        self.assertFalse(commission.a_verifier)
        self.assertTrue(Subscription.objects.filter(user=client).exists())

    def test_paiement_campay_reussi_cree_la_commission(self):
        client = self._client()
        paiement = Transaction.objects.create(
            user=client, profil=client.profils.first(), plan=self.plan, amount=15000,
            phone_number="699000333", provider_reference="campay-x", status=StatutTransaction.SUCCESSFUL,
        )
        paiement._confirmer_succes()

        commission = Commission.objects.get(transaction=paiement)
        self.assertEqual(commission.montant_fcfa, 2100)

    def test_enfant_supplementaire_a_12000_donne_1680(self):
        client = self._client()
        plan = Plan.objects.create(name="Autre", cursus=self.cursus, price=12000, duration_days=365)
        paiement = self._manuel(client, "REF-12K", plan=plan)

        commission = enregistrer_commission(paiement)

        self.assertEqual(commission.montant_fcfa, 1680)

    def test_arrondi_au_franc_inferieur(self):
        client = self._client()
        paiement = self._manuel(client, "REF-ARR", montant=1005)
        paiement.amount_expected = 1005
        paiement.save()

        self.assertEqual(enregistrer_commission(paiement).montant_fcfa, 140)

    def test_idempotent(self):
        client = self._client()
        paiement = self._manuel(client, "REF-IDEM")

        premiere = enregistrer_commission(paiement)
        seconde = enregistrer_commission(paiement)

        self.assertEqual(premiere.pk, seconde.pk)
        self.assertEqual(Commission.objects.count(), 1)

    def test_pas_de_commission_sans_attribution(self):
        client = self._client(attribue=False)
        self.assertIsNone(enregistrer_commission(self._manuel(client, "REF-SANS")))

    def test_pas_de_commission_pour_un_achat_couvert_par_du_credit(self):
        client = self._client()
        paiement = self._campay(client, montant=0)
        self.assertIsNone(enregistrer_commission(paiement))

    def test_pas_de_commission_pour_un_revendeur_en_attente_ou_resilie(self):
        client = self._client()
        for statut in (StatutRevendeur.EN_ATTENTE, StatutRevendeur.RESILIE):
            Revendeur.objects.filter(pk=self.revendeur.pk).update(statut=statut)
            self.assertIsNone(enregistrer_commission(self._manuel(client, f"REF-{statut}")), statut)

    def test_revendeur_suspendu_commission_retenue(self):
        client = self._client()
        Revendeur.objects.filter(pk=self.revendeur.pk).update(statut=StatutRevendeur.SUSPENDU)

        commission = enregistrer_commission(self._manuel(client, "REF-SUSP"))

        self.assertTrue(commission.a_verifier)
        self.assertIn("suspendu", commission.motif_a_verifier)

    def test_montant_declare_different_du_montant_attendu_retenu(self):
        client = self._client()
        commission = enregistrer_commission(self._manuel(client, "REF-DIFF", montant=14000))

        self.assertTrue(commission.a_verifier)
        self.assertEqual(commission.base_fcfa, 14000)

    def test_fenetre_de_12_mois(self):
        client = self._client(attribue=False)
        AttributionRevendeur.objects.create(
            client=client, revendeur=self.revendeur, attribue_le=timezone.now() - timedelta(days=364),
        )
        self.assertIsNotNone(enregistrer_commission(self._manuel(client, "REF-DANS")))

        AttributionRevendeur.objects.filter(client=client).update(attribue_le=timezone.now() - timedelta(days=366))
        self.assertIsNone(enregistrer_commission(self._manuel(client, "REF-HORS")))

    def test_plusieurs_paiements_du_meme_client_dans_la_fenetre_donnent_chacun_une_commission(self):
        client = self._client()
        enregistrer_commission(self._manuel(client, "REF-A"))
        enregistrer_commission(self._manuel(client, "REF-B"))

        self.assertEqual(Commission.objects.filter(client=client).count(), 2)


class AutoAchatTests(_Base):
    def test_le_revendeur_est_lui_meme_le_client(self):
        AttributionRevendeur.objects.create(client=self.revendeur.user, revendeur=self.revendeur)
        paiement = self._manuel(self.revendeur.user, "REF-MOI")
        self.assertIsNone(enregistrer_commission(paiement))

    def test_numero_payeur_identique_au_numero_de_versement(self):
        Revendeur.objects.filter(pk=self.revendeur.pk).update(numero_versement="699555444")
        client = self._client()
        paiement = self._manuel(client, "REF-PAYEUR", payeur="699555444")
        self.assertIsNone(enregistrer_commission(paiement))

    def test_numero_payeur_identique_au_telephone_du_compte_revendeur(self):
        client = self._client()
        paiement = self._manuel(client, "REF-PAYEUR2", payeur="677900001")
        self.assertIsNone(enregistrer_commission(paiement))

    def test_client_avec_le_meme_numero_que_le_revendeur_en_format_different(self):
        Revendeur.objects.filter(pk=self.revendeur.pk).update(numero_versement="699111222")
        client = User.objects.create_user(phone_number="+237699111222", password="x")
        AttributionRevendeur.objects.create(client=client, revendeur=self.revendeur)
        self.assertIsNone(enregistrer_commission(self._manuel(client, "REF-FMT")))


class PalierCommercialTests(_Base):
    def setUp(self):
        super().setUp()
        self.revendeur = _revendeur(tel="677900060", code="COMM01", type=TypeRevendeur.COMMERCIAL)

    def _ventes(self, n, depart=100):
        commissions = []
        for i in range(n):
            client = User.objects.create_user(phone_number=f"6779{depart + i:05d}", password="x")
            AttributionRevendeur.objects.create(client=client, revendeur=self.revendeur)
            commissions.append(enregistrer_commission(self._manuel(client, f"REF-P-{depart}-{i}")))
        return commissions

    def test_les_30_premieres_ventes_a_14_la_31e_a_17(self):
        commissions = self._ventes(31)

        self.assertEqual({c.taux_pct for c in commissions[:30]}, {14})
        self.assertEqual(commissions[30].taux_pct, 17)
        self.assertEqual(commissions[30].montant_fcfa, 2550)

    def test_une_annulation_libere_une_place_dans_le_mois(self):
        commissions = self._ventes(30)
        commissions[0].annuler("remboursement")

        self.assertEqual(self._ventes(1, depart=500)[0].taux_pct, 14)
        self.assertEqual(self._ventes(1, depart=600)[0].taux_pct, 17)

    def test_le_compteur_repart_chaque_mois(self):
        self._ventes(30)
        Commission.objects.filter(revendeur=self.revendeur).update(created_at=timezone.now() - timedelta(days=40))

        self.assertEqual(self._ventes(1, depart=700)[0].taux_pct, 14)

    def test_pas_de_palier_pour_un_repetiteur(self):
        repet = _revendeur(tel="677900061", code="REPET1", type=TypeRevendeur.REPETITEUR)
        for i in range(31):
            client = User.objects.create_user(phone_number=f"6779{800 + i:05d}", password="x")
            AttributionRevendeur.objects.create(client=client, revendeur=repet)
            commission = enregistrer_commission(self._manuel(client, f"REF-R-{i}"))
        self.assertEqual(commission.taux_pct, 14)


class AnnulationTests(_Base):
    def _commission(self):
        return enregistrer_commission(self._manuel(self._client(), "REF-ANN"))

    def test_annulation_avant_acquisition(self):
        commission = self._commission()
        commission.annuler("remboursement")

        commission.refresh_from_db()
        self.assertEqual(commission.statut, StatutCommission.ANNULEE)
        self.assertEqual(commission.etat, "ANNULEE")

    def test_commission_acquise_apres_14_jours(self):
        commission = self._commission()
        Commission.objects.filter(pk=commission.pk).update(acquise_le=timezone.now() - timedelta(seconds=1))
        commission.refresh_from_db()

        self.assertEqual(commission.etat, "ACQUISE")

    def test_annulation_apres_acquisition_refusee_sauf_fraude(self):
        commission = self._commission()
        Commission.objects.filter(pk=commission.pk).update(acquise_le=timezone.now() - timedelta(days=1))
        commission.refresh_from_db()

        with self.assertRaises(CommissionDejaAcquise):
            commission.annuler("regret")
        commission.annuler("fraude avérée", fraude=True)

        self.assertEqual(commission.statut, StatutCommission.ANNULEE)

    def test_double_annulation_refusee(self):
        commission = self._commission()
        commission.annuler("x")
        with self.assertRaises(ValueError):
            commission.annuler("x")


class CommissionNeBloquePasLAccesTests(_Base):
    def test_une_erreur_de_commission_n_empeche_pas_l_activation(self):
        client = self._client()
        paiement = self._manuel(client, "REF-PANNE")

        with patch("revendeurs.services.enregistrer_commission", side_effect=RuntimeError("boum")):
            with self.assertLogs("revendeurs.services", level="ERROR"):
                paiement.approve(self.admin)

        paiement.refresh_from_db()
        self.assertEqual(paiement.status, "APPROVED")
        self.assertTrue(Subscription.objects.filter(user=client).exists())
        self.assertEqual(Commission.objects.count(), 0)

    def test_le_enveloppe_retourne_none_en_cas_d_erreur(self):
        client = self._client()
        paiement = self._manuel(client, "REF-PANNE2")
        with patch("revendeurs.services.enregistrer_commission", side_effect=RuntimeError("boum")):
            with self.assertLogs("revendeurs.services", level="ERROR"):
                self.assertIsNone(enregistrer_commission_securise(paiement))

    def test_un_paiement_rejete_ne_donne_aucune_commission(self):
        from payments.models import ManualPaymentRejectReason

        client = self._client()
        paiement = self._manuel(client, "REF-REJ")
        paiement.reject(self.admin, ManualPaymentRejectReason.PAIEMENT_NON_RECU)

        self.assertEqual(Commission.objects.count(), 0)


class MasquerClientTests(TestCase):
    def test_initiales_et_fin_du_numero(self):
        user = User.objects.create_user(phone_number="677123456", password="x", full_name="Awa Nkoulou Bela")
        self.assertEqual(masquer_client(user), "A. N. ••3456")

    def test_compte_sans_nom_ni_telephone(self):
        user = User.objects.create_user(phone_number=None, email="eleve@example.com", email_verified=True)
        self.assertEqual(masquer_client(user), "e•••")

    def test_ne_laisse_filtrer_ni_le_numero_complet_ni_l_adresse(self):
        user = User.objects.create_user(phone_number="677123456", password="x", full_name="Awa N")
        self.assertNotIn("677123456", masquer_client(user))
        self.assertNotIn("123", masquer_client(user).replace("3456", ""))


class EspaceRevendeurAPITests(_Base):
    def setUp(self):
        super().setUp()
        self.api = APIClient()

    def _vente(self, tel, ref, **commission_extra):
        client = self._client(tel=tel)
        commission = enregistrer_commission(self._manuel(client, ref))
        if commission_extra:
            Commission.objects.filter(pk=commission.pk).update(**commission_extra)
        return commission

    def test_refuse_sans_connexion(self):
        self.assertEqual(self.api.get("/revendeurs/moi/").status_code, 401)

    def test_un_compte_non_revendeur_recoit_404(self):
        self.api.force_authenticate(self.admin)
        self.assertEqual(self.api.get("/revendeurs/moi/").status_code, 404)
        self.assertEqual(self.api.get("/revendeurs/moi/ventes/").status_code, 404)

    def test_tableau_de_bord(self):
        self._vente("677900071", "REF-D1")  # en attente
        self._vente("677900072", "REF-D2", acquise_le=timezone.now() - timedelta(days=1))  # acquise
        self._vente("677900073", "REF-D3", a_verifier=True)  # retenue
        annulee = self._vente("677900074", "REF-D4")
        annulee.annuler("test")
        self.api.force_authenticate(self.revendeur.user)

        data = self.api.get("/revendeurs/moi/").json()

        self.assertEqual(data["code"], "DEMO42")
        self.assertEqual(data["taux_base_pct"], 14)
        self.assertEqual(data["nb_clients"], 4)
        self.assertEqual(data["ventes_du_mois"], 3)
        self.assertEqual(data["montants"], {"en_attente": 2100, "acquise": 2100, "retenue": 2100, "payee": 0})
        self.assertIsNone(data["palier"])

    def test_palier_expose_pour_un_commercial(self):
        commercial = _revendeur(tel="677900080", code="COMM02", type=TypeRevendeur.COMMERCIAL)
        self.api.force_authenticate(commercial.user)

        self.assertEqual(self.api.get("/revendeurs/moi/").json()["palier"], {"seuil": 30, "taux_pct": 17})

    def test_ventes_masquent_le_client_et_ne_montrent_que_les_siennes(self):
        self._vente("677900075", "REF-V1")
        autre = _revendeur(tel="677900081", code="AUTRE2")
        etranger = User.objects.create_user(phone_number="677900082", password="x")
        AttributionRevendeur.objects.create(client=etranger, revendeur=autre)
        enregistrer_commission(self._manuel(etranger, "REF-V2"))
        self.api.force_authenticate(self.revendeur.user)

        data = self.api.get("/revendeurs/moi/ventes/").json()

        self.assertEqual(data["count"], 1)
        ligne = data["results"][0]
        self.assertEqual(ligne["montant_fcfa"], 2100)
        self.assertEqual(ligne["etat"], "EN_ATTENTE")
        self.assertNotIn("677900075", str(ligne))
        self.assertTrue(ligne["client"].endswith("0075"))

    def test_une_vente_retenue_est_signalee_sans_dire_pourquoi(self):
        self._vente("677900076", "REF-V3", a_verifier=True, motif_a_verifier="montant suspect")
        self.api.force_authenticate(self.revendeur.user)

        ligne = self.api.get("/revendeurs/moi/ventes/").json()["results"][0]

        self.assertEqual(ligne["etat"], "RETENUE")
        self.assertNotIn("suspect", str(ligne))


class RattachementAPITests(_Base):
    def setUp(self):
        super().setUp()
        self.api = APIClient()
        self.eleve = User.objects.create_user(phone_number="677900090", password="x")
        self.api.force_authenticate(self.eleve)

    def test_get_propose_la_saisie_a_un_compte_neuf(self):
        data = self.api.get("/revendeurs/rattachement/").json()
        self.assertEqual(data, {"peut_saisir_code": True, "revendeur": None})

    def test_post_rattache_et_ferme_la_saisie(self):
        reponse = self.api.post("/revendeurs/rattachement/", {"code": "demo42"}, format="json")

        self.assertEqual(reponse.status_code, 201)
        self.assertEqual(reponse.json()["revendeur"]["nom_affiche"], self.revendeur.nom_affiche)
        self.assertEqual(AttributionRevendeur.objects.get(client=self.eleve).source, SourceAttribution.PAIEMENT)
        data = self.api.get("/revendeurs/rattachement/").json()
        self.assertFalse(data["peut_saisir_code"])
        self.assertEqual(data["revendeur"]["nom_affiche"], self.revendeur.nom_affiche)

    def test_code_inconnu_et_code_inactif_donnent_la_meme_reponse(self):
        Revendeur.objects.filter(pk=self.revendeur.pk).update(statut=StatutRevendeur.SUSPENDU)
        inconnu = self.api.post("/revendeurs/rattachement/", {"code": "NOPE99"}, format="json")
        inactif = self.api.post("/revendeurs/rattachement/", {"code": "DEMO42"}, format="json")

        self.assertEqual((inconnu.status_code, inconnu.json()), (400, {"code": "code_invalide"}))
        self.assertEqual((inactif.status_code, inactif.json()), (400, {"code": "code_invalide"}))

    def test_apres_un_paiement_valide_la_saisie_est_fermee(self):
        self._manuel(self.eleve, "REF-RATT").approve(self.admin)

        self.assertFalse(self.api.get("/revendeurs/rattachement/").json()["peut_saisir_code"])
        self.assertEqual(self.api.post("/revendeurs/rattachement/", {"code": "DEMO42"}, format="json").status_code, 400)

    def test_une_fois_attribue_un_autre_code_est_refuse(self):
        autre = _revendeur(tel="677900091", code="AUTRE3")
        self.api.post("/revendeurs/rattachement/", {"code": "DEMO42"}, format="json")

        self.assertEqual(self.api.post("/revendeurs/rattachement/", {"code": autre.code}, format="json").status_code, 400)
        self.assertEqual(AttributionRevendeur.objects.get(client=self.eleve).revendeur, self.revendeur)

    def test_commission_creee_au_paiement_suivant(self):
        self.api.post("/revendeurs/rattachement/", {"code": "DEMO42"}, format="json")
        self._manuel(self.eleve, "REF-APRES").approve(self.admin)

        self.assertEqual(Commission.objects.get().montant_fcfa, 2100)

    def test_plafond_de_saisies(self):
        from django.core.cache import cache

        from .views import RattachementThrottle

        cache.clear()
        with override_settings(THROTTLE_PDF_ACTIF=True), patch.object(RattachementThrottle, "rate", "2/hour"):
            codes = [self.api.post("/revendeurs/rattachement/", {"code": "NOPE99"}, format="json").status_code for _ in range(3)]
            lecture = self.api.get("/revendeurs/rattachement/").status_code
        cache.clear()

        self.assertEqual(codes, [400, 400, 429])
        self.assertEqual(lecture, 200)
