"""
Décision depuis la liste admin des paiements manuels : filtre par défaut, boutons par
ligne (page de confirmation, mutation en POST uniquement), actions groupées et leurs
garde-fous. approve()/reject() sont déjà couverts dans tests.py - ici, seule la couche
admin qui les appelle.
"""

from django.test import TestCase
from django.urls import reverse

from catalog.models import Cursus, Examen
from subscriptions.models import Plan, Subscription
from users.models import User

from .models import (
    ManualPayment,
    ManualPaymentRejectReason,
    ManualPaymentStatus,
    MobileMoneyOperator,
)


class ManualPaymentAdminDecisionTests(TestCase):
    def setUp(self):
        self.cursus = Cursus.objects.get(examen=Examen.BAC, series__code="C")
        self.admin = User.objects.create_superuser(phone_number="677000051", password="x")
        self.client.force_login(self.admin)
        self.user = User.objects.create_user(phone_number="677000050", password="x")
        self.plan = Plan.objects.create(name="Trimestre", cursus=self.cursus, price=2000, duration_days=90)
        self.liste = reverse("admin:payments_manualpayment_changelist")

    def _paiement(self, reference, declared=None, status=ManualPaymentStatus.PENDING):
        return ManualPayment.objects.create(
            user=self.user, profil=self.user.profils.first(), plan=self.plan,
            operator=MobileMoneyOperator.ORANGE, amount_expected=self.plan.price,
            amount_declared=declared or self.plan.price, payer_phone_number=self.user.phone_number,
            transaction_reference=reference, status=status,
        )

    def _decider(self, payment, action):
        return reverse("admin:payments_manualpayment_decider", args=[payment.pk, action])

    def test_menu_payments_est_epingle_en_tete(self):
        reponse = self.client.get(reverse("admin:index"))

        apps = reponse.context["app_list"]
        self.assertEqual(apps[0]["app_label"], "payments")
        autres = [str(app["name"]).lower() for app in apps[1:]]
        self.assertEqual(autres, sorted(autres))

    def test_liste_par_defaut_n_affiche_que_les_paiements_en_attente(self):
        en_attente = self._paiement("OM-ADM-1")
        rejete = self._paiement("OM-ADM-2", status=ManualPaymentStatus.REJECTED)

        reponse = self.client.get(self.liste)
        self.assertEqual([p.pk for p in reponse.context["cl"].result_list], [en_attente.pk])

        reponse = self.client.get(self.liste, {"statut": "all"})
        self.assertEqual({p.pk for p in reponse.context["cl"].result_list}, {en_attente.pk, rejete.pk})

    def test_recherche_sans_filtre_porte_sur_tous_les_statuts(self):
        rejete = self._paiement("OM-ADM-3", status=ManualPaymentStatus.REJECTED)

        reponse = self.client.get(self.liste, {"q": "OM-ADM-3"})

        self.assertEqual([p.pk for p in reponse.context["cl"].result_list], [rejete.pk])

    def test_liste_en_attente_du_plus_ancien_au_plus_recent(self):
        premier = self._paiement("OM-ADM-4")
        second = self._paiement("OM-ADM-5")

        reponse = self.client.get(self.liste)

        self.assertEqual([p.pk for p in reponse.context["cl"].result_list], [premier.pk, second.pk])

    def test_liste_affiche_les_boutons_de_decision(self):
        paiement = self._paiement("OM-ADM-5B")

        reponse = self.client.get(self.liste)

        self.assertContains(reponse, self._decider(paiement, "valider"))
        self.assertContains(reponse, self._decider(paiement, "rejeter"))

    def test_page_de_confirmation_ne_modifie_rien(self):
        paiement = self._paiement("OM-ADM-6")

        reponse = self.client.get(self._decider(paiement, "valider"))

        self.assertEqual(reponse.status_code, 200)
        paiement.refresh_from_db()
        self.assertEqual(paiement.status, ManualPaymentStatus.PENDING)
        self.assertFalse(Subscription.objects.filter(user=self.user).exists())

    def test_valider_en_post_active_labonnement_et_revient_a_la_liste(self):
        paiement = self._paiement("OM-ADM-7")
        retour = f"{self.liste}?statut=PENDING&o=1"

        reponse = self.client.post(self._decider(paiement, "valider"), {"next": retour})

        self.assertRedirects(reponse, retour, fetch_redirect_response=False)
        paiement.refresh_from_db()
        self.assertEqual(paiement.status, ManualPaymentStatus.APPROVED)
        self.assertEqual(paiement.reviewed_by, self.admin)
        self.assertTrue(Subscription.objects.get(user=self.user, cursus=self.cursus).is_active)

    def test_rejet_sans_motif_est_refuse(self):
        paiement = self._paiement("OM-ADM-8")

        reponse = self.client.post(self._decider(paiement, "rejeter"), {})

        self.assertEqual(reponse.status_code, 200)
        paiement.refresh_from_db()
        self.assertEqual(paiement.status, ManualPaymentStatus.PENDING)

    def test_rejet_avec_motif(self):
        paiement = self._paiement("OM-ADM-9")

        self.client.post(self._decider(paiement, "rejeter"), {
            "rejection_reason": ManualPaymentRejectReason.PAIEMENT_NON_RECU, "admin_comment": "rien vu",
        })

        paiement.refresh_from_db()
        self.assertEqual(paiement.status, ManualPaymentStatus.REJECTED)
        self.assertEqual(paiement.rejection_reason, ManualPaymentRejectReason.PAIEMENT_NON_RECU)
        self.assertEqual(paiement.admin_comment, "rien vu")
        self.assertFalse(Subscription.objects.filter(user=self.user).exists())

    def test_paiement_deja_traite_n_est_pas_retraite(self):
        paiement = self._paiement("OM-ADM-10")
        paiement.approve(admin_user=self.admin)
        expiration = Subscription.objects.get(user=self.user, cursus=self.cursus).expires_at

        self.client.post(self._decider(paiement, "valider"), {"next": self.liste})

        self.assertEqual(Subscription.objects.get(user=self.user, cursus=self.cursus).expires_at, expiration)

    def test_next_externe_est_ignore(self):
        paiement = self._paiement("OM-ADM-11")

        reponse = self.client.post(self._decider(paiement, "valider"), {"next": "https://evil.example/"})

        self.assertRedirects(reponse, self.liste, fetch_redirect_response=False)

    def test_non_staff_ne_peut_pas_decider(self):
        paiement = self._paiement("OM-ADM-12")
        self.client.force_login(self.user)

        self.client.post(self._decider(paiement, "valider"))

        paiement.refresh_from_db()
        self.assertEqual(paiement.status, ManualPaymentStatus.PENDING)

    def test_action_inconnue_est_refusee(self):
        paiement = self._paiement("OM-ADM-13")

        reponse = self.client.post(self._decider(paiement, "supprimer"))

        self.assertEqual(reponse.status_code, 403)

    def test_validation_groupee_demande_confirmation_puis_exclut_les_montants_incoherents(self):
        propre = self._paiement("OM-ADM-14")
        incoherent = self._paiement("OM-ADM-15", declared=2500)
        donnees = {"action": "valider_selection", "_selected_action": [propre.pk, incoherent.pk]}

        confirmation = self.client.post(self.liste, donnees)
        self.assertEqual(confirmation.status_code, 200)
        propre.refresh_from_db()
        self.assertEqual(propre.status, ManualPaymentStatus.PENDING)  # rien avant la confirmation
        self.assertEqual([i["payment"].pk for i in confirmation.context["exclus"]], [incoherent.pk])

        self.client.post(self.liste, {**donnees, "post": "yes"})
        propre.refresh_from_db()
        incoherent.refresh_from_db()
        self.assertEqual(propre.status, ManualPaymentStatus.APPROVED)
        self.assertEqual(incoherent.status, ManualPaymentStatus.PENDING)

    def test_rejet_groupe_exige_un_motif_commun(self):
        a = self._paiement("OM-ADM-16")
        b = self._paiement("OM-ADM-17")
        donnees = {"action": "rejeter_selection", "_selected_action": [a.pk, b.pk], "post": "yes"}

        self.client.post(self.liste, donnees)
        a.refresh_from_db()
        self.assertEqual(a.status, ManualPaymentStatus.PENDING)

        self.client.post(self.liste, {**donnees, "rejection_reason": ManualPaymentRejectReason.MONTANT_INCORRECT})
        a.refresh_from_db()
        b.refresh_from_db()
        self.assertEqual(a.status, ManualPaymentStatus.REJECTED)
        self.assertEqual(b.status, ManualPaymentStatus.REJECTED)

    def test_reference_deja_vue_exclut_de_la_validation_groupee(self):
        ancien = self._paiement("OM-ADM-18", status=ManualPaymentStatus.REJECTED)
        nouveau = self._paiement("OM-ADM-18")
        self.assertNotEqual(ancien.pk, nouveau.pk)

        self.client.post(self.liste, {
            "action": "valider_selection", "_selected_action": [nouveau.pk], "post": "yes",
        })

        nouveau.refresh_from_db()
        self.assertEqual(nouveau.status, ManualPaymentStatus.PENDING)
