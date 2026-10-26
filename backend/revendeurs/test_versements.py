"""Phase 3 : signaux de fraude, versements mensuels, reprises, admin et API « Mes versements »."""
from datetime import timedelta
from unittest.mock import patch

from django.test import Client
from django.utils import timezone
from rest_framework.test import APIClient

from payments.models import ManualPayment, ManualPaymentStatus
from users.models import User

from .models import Commission, CommissionDejaAcquise, Revendeur, StatutCommission, StatutRevendeur, StatutVersement, Versement
from .services import (
    VersementImpossible,
    annuler_versement,
    enregistrer_commission,
    exporter_csv,
    marquer_paye,
    preparer_versement,
    preparer_versements,
    reprises_dues,
)
from .tests import _Base, _revendeur


class SignauxDeFraudeTests(_Base):
    def _attribue(self, tel):
        return self._client(tel=tel)

    def test_une_vente_ordinaire_n_est_pas_retenue(self):
        commission = enregistrer_commission(self._manuel(self._attribue("677900301"), "REF-N1"))
        self.assertFalse(commission.a_verifier)

    def test_meme_adresse_ip(self):
        dernier = None
        for i, tel in enumerate(("677900311", "677900321", "677900331")):
            dernier = self._manuel(self._attribue(tel), f"REF-IP{i}")
            ManualPayment.objects.filter(pk=dernier.pk).update(declared_ip="41.202.10.5")
        commission = enregistrer_commission(ManualPayment.objects.get(pk=dernier.pk))

        self.assertTrue(commission.a_verifier)
        self.assertIn("adresse IP", commission.motif_a_verifier)

    def test_deux_clients_sur_la_meme_ip_ne_declenchent_rien(self):
        for i, tel in enumerate(("677900341", "677900351")):
            p = self._manuel(self._attribue(tel), f"REF-IP2{i}")
            ManualPayment.objects.filter(pk=p.pk).update(declared_ip="41.202.10.6")
        self.assertFalse(enregistrer_commission(ManualPayment.objects.get(transaction_reference="REF-IP21")).a_verifier)

    def test_meme_payeur_pour_trois_comptes(self):
        dernier = None
        for i, tel in enumerate(("677900361", "677900371", "677900381")):
            dernier = self._manuel(self._attribue(tel), f"REF-PY{i}", payeur="699555111")
        commission = enregistrer_commission(dernier)

        self.assertTrue(commission.a_verifier)
        self.assertIn("même numéro", commission.motif_a_verifier)

    def test_un_parent_qui_paie_pour_plusieurs_enfants_du_meme_compte_n_est_pas_signale(self):
        client = self._attribue("677900391")
        enregistrer_commission(self._manuel(client, "REF-FAM1", payeur="699555222"))
        enregistrer_commission(self._manuel(client, "REF-FAM2", payeur="699555222"))
        commission = enregistrer_commission(self._manuel(client, "REF-FAM3", payeur="699555222"))

        self.assertFalse(commission.a_verifier)

    def test_numeros_qui_se_suivent(self):
        for tel in ("677900401", "677900403"):
            self._attribue(tel)
        milieu = self._attribue("677900402")
        commission = enregistrer_commission(self._manuel(milieu, "REF-NV"))

        self.assertTrue(commission.a_verifier)
        self.assertIn("se suivent", commission.motif_a_verifier)

    def test_un_seul_voisin_ne_suffit_pas(self):
        self._attribue("677900411")
        commission = enregistrer_commission(self._manuel(self._attribue("677900412"), "REF-NV2"))
        self.assertFalse(commission.a_verifier)

    def test_paiements_refuses_en_serie(self):
        for i, tel in enumerate(("677900421", "677900431", "677900441")):
            p = self._manuel(self._attribue(tel), f"REF-RJ{i}")
            ManualPayment.objects.filter(pk=p.pk).update(status=ManualPaymentStatus.REJECTED)
        commission = enregistrer_commission(self._manuel(self._attribue("677900451"), "REF-RJ-OK"))

        self.assertTrue(commission.a_verifier)
        self.assertIn("refusés", commission.motif_a_verifier)

    def test_pic_d_inscriptions_le_meme_jour(self):
        with patch("revendeurs.fraude.FRAUDE_PIC_INSCRIPTIONS_SEUIL", 3):
            for tel in ("677900461", "677900471"):
                self._attribue(tel)
            commission = enregistrer_commission(self._manuel(self._attribue("677900481"), "REF-PIC"))

        self.assertTrue(commission.a_verifier)
        self.assertIn("le même jour", commission.motif_a_verifier)

    def test_les_signaux_sont_cumules_avec_les_autres_motifs(self):
        Revendeur.objects.filter(pk=self.revendeur.pk).update(statut=StatutRevendeur.SUSPENDU)
        with patch("revendeurs.fraude.FRAUDE_PIC_INSCRIPTIONS_SEUIL", 1):
            commission = enregistrer_commission(self._manuel(self._attribue("677900491"), "REF-CUMUL"))

        self.assertIn("suspendu", commission.motif_a_verifier)
        self.assertIn("le même jour", commission.motif_a_verifier)


class _FabriqueVersements(_Base):
    def _acquise(self, tel, ref, **extra):
        """Une vente de 2 100 FCFA de commission, déjà acquise."""
        client = self._client(tel=tel)
        commission = enregistrer_commission(self._manuel(client, ref))
        Commission.objects.filter(pk=commission.pk).update(acquise_le=timezone.now() - timedelta(days=1), **extra)
        commission.refresh_from_db()
        return commission

    def _trois_ventes(self, debut=500):
        # Numéros espacés : des numéros qui se suivent retiendraient les commissions (voir SignauxDeFraudeTests).
        return [self._acquise(f"6779{debut + 10 * i:05d}", f"REF-VT-{debut}-{i}") for i in range(3)]

    def _pret(self):
        Revendeur.objects.filter(pk=self.revendeur.pk).update(numero_versement="699111222", operateur_versement="ORANGE")
        self.revendeur.refresh_from_db()


class VersementsTests(_FabriqueVersements):
    def test_prepare_les_commissions_acquises(self):
        self._pret()
        commissions = self._trois_ventes()

        versement, raison = preparer_versement(self.revendeur)

        self.assertIsNone(raison)
        self.assertEqual((versement.montant_brut, versement.montant_reprises, versement.montant_net), (6300, 0, 6300))
        self.assertEqual((versement.operateur, versement.numero), ("ORANGE", "699111222"))
        self.assertEqual(versement.statut, StatutVersement.PREPARE)
        for c in commissions:
            c.refresh_from_db()
            self.assertEqual(c.versement, versement)

    def test_sous_le_seuil_le_solde_est_reporte(self):
        self._pret()
        self._acquise("677900601", "REF-SEUIL1")
        self._acquise("677900611", "REF-SEUIL2")

        versement, raison = preparer_versement(self.revendeur)

        self.assertIsNone(versement)
        self.assertIn("seuil", raison)
        self.assertFalse(Versement.objects.exists())
        self.assertEqual(Commission.objects.filter(versement__isnull=True).count(), 2)

    def test_ignore_les_commissions_en_attente_retenues_et_annulees(self):
        self._pret()
        self._trois_ventes()
        enregistrer_commission(self._manuel(self._client(tel="677900701"), "REF-ATT"))  # pas encore acquise
        self._acquise("677900711", "REF-RET", a_verifier=True)
        self._acquise("677900721", "REF-ANN").annuler("remboursement", fraude=True)

        versement, _ = preparer_versement(self.revendeur)

        self.assertEqual(versement.montant_brut, 6300)

    def test_refuse_un_revendeur_sans_numero_suspendu_ou_en_attente(self):
        self._trois_ventes()
        self.assertEqual(preparer_versement(self.revendeur)[1], "numéro de versement manquant")
        self._pret()
        Revendeur.objects.filter(pk=self.revendeur.pk).update(statut=StatutRevendeur.SUSPENDU)
        self.assertEqual(preparer_versement(self.revendeur)[1], "revendeur suspendu")
        Revendeur.objects.filter(pk=self.revendeur.pk).update(statut=StatutRevendeur.EN_ATTENTE)
        self.assertEqual(preparer_versement(self.revendeur)[1], "compte pas encore activé")

    def test_un_seul_versement_en_cours(self):
        self._pret()
        self._trois_ventes()
        preparer_versement(self.revendeur)
        self._trois_ventes(debut=800)

        versement, raison = preparer_versement(self.revendeur)

        self.assertIsNone(versement)
        self.assertEqual(raison, "un versement est déjà préparé")

    def test_marquer_paye_exige_une_reference_puis_regle_les_commissions(self):
        self._pret()
        commissions = self._trois_ventes()
        versement, _ = preparer_versement(self.revendeur)

        with self.assertRaises(VersementImpossible):
            marquer_paye(versement, self.admin, "  ")
        paye = marquer_paye(versement, self.admin, "MP261026.1234.A56789", frais_retrait=150)

        self.assertEqual((paye.statut, paye.reference_mobile_money, paye.frais_retrait), (StatutVersement.PAYE, "MP261026.1234.A56789", 150))
        self.assertEqual(paye.paye_par, self.admin)
        for c in commissions:
            c.refresh_from_db()
            self.assertEqual(c.statut, StatutCommission.PAYEE)

    def test_marquer_paye_deux_fois_est_refuse(self):
        self._pret()
        self._trois_ventes()
        versement, _ = preparer_versement(self.revendeur)
        marquer_paye(versement, self.admin, "REF1")

        with self.assertRaises(VersementImpossible):
            marquer_paye(versement, self.admin, "REF2")

    def test_le_revendeur_est_prevenu_par_sms(self):
        self._pret()
        self._trois_ventes()
        versement, _ = preparer_versement(self.revendeur)

        with patch("users.sms_backends.get_sms_backend") as backend:
            marquer_paye(versement, self.admin, "REF-SMS")

        envoye = backend.return_value.send.call_args.args
        self.assertEqual(envoye[0], self.revendeur.user.phone_number)
        self.assertIn("6300", envoye[1])
        self.assertIn("REF-SMS", envoye[1])

    def test_un_sms_en_echec_ne_defait_pas_le_versement(self):
        self._pret()
        self._trois_ventes()
        versement, _ = preparer_versement(self.revendeur)

        with patch("users.sms_backends.get_sms_backend", side_effect=RuntimeError("opérateur HS")):
            with self.assertLogs("revendeurs.services", level="ERROR"):
                marquer_paye(versement, self.admin, "REF-SMS2")

        versement.refresh_from_db()
        self.assertEqual(versement.statut, StatutVersement.PAYE)

    def test_annuler_un_versement_libere_les_commissions(self):
        self._pret()
        self._trois_ventes()
        versement, _ = preparer_versement(self.revendeur)

        annuler_versement(versement)

        versement.refresh_from_db()
        self.assertEqual(versement.statut, StatutVersement.ANNULE)
        self.assertEqual(Commission.objects.filter(versement__isnull=False).count(), 0)
        self.assertIsNotNone(preparer_versement(self.revendeur)[0])

    def test_une_commission_d_un_versement_prepare_ne_s_annule_pas(self):
        self._pret()
        commissions = self._trois_ventes()
        preparer_versement(self.revendeur)
        commissions[0].refresh_from_db()

        with self.assertRaises(ValueError):
            commissions[0].annuler("fraude", fraude=True)

    def test_fraude_apres_paiement_deduite_du_versement_suivant(self):
        self._pret()
        premieres = self._trois_ventes()
        versement, _ = preparer_versement(self.revendeur)
        marquer_paye(versement, self.admin, "REF-1")
        premieres[0].refresh_from_db()
        premieres[0].annuler("fraude avérée", fraude=True)  # 2 100 FCFA déjà reçus à reprendre
        premieres[0].refresh_from_db()
        self.assertTrue(premieres[0].a_reprendre)

        self._trois_ventes(debut=900)
        self._acquise("677901500", "REF-VT-4E")  # 4 ventes : 8 400 FCFA, moins 2 100 de reprise
        suivant, _ = preparer_versement(self.revendeur)

        self.assertEqual((suivant.montant_brut, suivant.montant_reprises, suivant.montant_net), (8400, 2100, 6300))
        premieres[0].refresh_from_db()
        self.assertEqual(premieres[0].reprise_dans, suivant)
        self.assertFalse(premieres[0].a_reprendre)

    def test_reprise_plus_grosse_que_le_solde_reportee(self):
        self._pret()
        premieres = self._trois_ventes()
        versement, _ = preparer_versement(self.revendeur)
        marquer_paye(versement, self.admin, "REF-1")
        for c in premieres:
            c.refresh_from_db()
            c.annuler("fraude", fraude=True)  # 6 300 FCFA à reprendre
        self._trois_ventes(debut=900)  # 6 300 FCFA de nouvelles commissions : net 0

        versement, raison = preparer_versement(self.revendeur)

        self.assertIsNone(versement)
        self.assertIn("seuil", raison)
        self.assertEqual(sum(c.montant_fcfa for c in reprises_dues(self.revendeur)), 6300)

    def test_une_commission_payee_ne_s_annule_pas_sans_fraude(self):
        self._pret()
        premieres = self._trois_ventes()
        versement, _ = preparer_versement(self.revendeur)
        marquer_paye(versement, self.admin, "REF-1")
        premieres[0].refresh_from_db()

        with self.assertRaises(CommissionDejaAcquise):
            premieres[0].annuler("regret")

    def test_preparer_versements_rend_les_raisons(self):
        self._pret()
        self._trois_ventes()
        sans_numero = _revendeur(tel="677900991", code="SANSNUM")

        versements, ignores = preparer_versements([self.revendeur, sans_numero])

        self.assertEqual(len(versements), 1)
        self.assertEqual(ignores, [(sans_numero, "numéro de versement manquant")])

    def test_export_csv(self):
        self._pret()
        self._trois_ventes()
        versement, _ = preparer_versement(self.revendeur)

        lignes = exporter_csv([versement]).strip().splitlines()

        self.assertEqual(lignes[0], "reference,operateur,numero,montant_fcfa,beneficiaire,periode")
        self.assertEqual(lignes[1], f"EDK-V{versement.pk},ORANGE,699111222,6300,{self.revendeur.nom_affiche},{versement.periode}")

    def test_commande_simuler_n_ecrit_rien(self):
        from io import StringIO

        from django.core.management import call_command

        self._pret()
        self._trois_ventes()
        sortie = StringIO()

        call_command("preparer_versements", "--simuler", stdout=sortie)

        self.assertIn("brut 6300", sortie.getvalue())
        self.assertFalse(Versement.objects.exists())

    def test_commande_prepare(self):
        from io import StringIO

        from django.core.management import call_command

        self._pret()
        self._trois_ventes()
        sortie = StringIO()

        call_command("preparer_versements", stdout=sortie)

        self.assertEqual(Versement.objects.count(), 1)
        self.assertIn("1 versement(s) préparé(s)", sortie.getvalue())


class VersementsAPIEtAdminTests(_FabriqueVersements):
    def setUp(self):
        super().setUp()
        self.api = APIClient()

    def _superuser(self, tel):
        client = Client()
        client.force_login(User.objects.create_superuser(phone_number=tel, password="x"))
        return client

    def test_mes_versements_masquent_les_annules_et_la_reference_avant_paiement(self):
        self._pret()
        self._trois_ventes()
        versement, _ = preparer_versement(self.revendeur)
        self.api.force_authenticate(self.revendeur.user)

        avant = self.api.get("/revendeurs/moi/versements/").json()["results"]
        marquer_paye(versement, self.admin, "REF-API")
        apres = self.api.get("/revendeurs/moi/versements/").json()["results"]

        self.assertEqual((avant[0]["statut"], avant[0]["reference"]), ("PREPARE", ""))
        self.assertEqual((apres[0]["statut"], apres[0]["reference"], apres[0]["montant_net"]), ("PAYE", "REF-API", 6300))
        self.assertNotIn("numero", apres[0])

    def test_un_versement_annule_n_apparait_pas(self):
        self._pret()
        self._trois_ventes()
        versement, _ = preparer_versement(self.revendeur)
        annuler_versement(versement)
        self.api.force_authenticate(self.revendeur.user)

        self.assertEqual(self.api.get("/revendeurs/moi/versements/").json()["count"], 0)

    def test_un_non_revendeur_recoit_404(self):
        self.api.force_authenticate(self.admin)
        self.assertEqual(self.api.get("/revendeurs/moi/versements/").status_code, 404)

    def test_un_revendeur_ne_voit_pas_les_versements_d_un_autre(self):
        self._pret()
        self._trois_ventes()
        preparer_versement(self.revendeur)
        autre = _revendeur(tel="677900981", code="AUTRE9")
        self.api.force_authenticate(autre.user)

        self.assertEqual(self.api.get("/revendeurs/moi/versements/").json()["count"], 0)

    def test_le_tableau_de_bord_annonce_les_reprises_en_cours(self):
        self._pret()
        premieres = self._trois_ventes()
        versement, _ = preparer_versement(self.revendeur)
        marquer_paye(versement, self.admin, "REF-1")
        premieres[0].refresh_from_db()
        premieres[0].annuler("fraude", fraude=True)
        self.api.force_authenticate(self.revendeur.user)

        data = self.api.get("/revendeurs/moi/").json()

        self.assertEqual(data["reprises_en_cours"], 2100)
        self.assertEqual(data["montants"]["payee"], 4200)

    def test_pages_d_admin_sans_erreur(self):
        self._pret()
        self._trois_ventes()
        versement, _ = preparer_versement(self.revendeur)
        client = self._superuser("677900999")

        for url in (
            "/admin/revendeurs/revendeur/", "/admin/revendeurs/commission/", "/admin/revendeurs/versement/",
            "/admin/revendeurs/attributionrevendeur/",
        ):
            self.assertEqual(client.get(url).status_code, 200, url)
        self.assertEqual(client.get(f"/admin/revendeurs/versement/{versement.pk}/change/").status_code, 200)

    def test_actions_d_admin_sur_les_versements(self):
        self._pret()
        self._trois_ventes()
        versement, _ = preparer_versement(self.revendeur)
        client = self._superuser("677900998")
        url = "/admin/revendeurs/versement/"

        csv = client.post(url, {"action": "exporter_en_csv", "_selected_action": [versement.pk]})
        self.assertEqual(csv.status_code, 200)
        self.assertIn("EDK-V", csv.content.decode())

        client.post(url, {"action": "marquer_comme_paye", "_selected_action": [versement.pk]})
        versement.refresh_from_db()
        self.assertEqual(versement.statut, StatutVersement.PREPARE)  # pas de référence saisie

        Versement.objects.filter(pk=versement.pk).update(reference_mobile_money="REF-ADMIN")
        client.post(url, {"action": "marquer_comme_paye", "_selected_action": [versement.pk]})
        versement.refresh_from_db()
        self.assertEqual(versement.statut, StatutVersement.PAYE)

    def test_action_preparer_depuis_la_liste_des_revendeurs(self):
        self._pret()
        self._trois_ventes()
        client = self._superuser("677900997")

        client.post("/admin/revendeurs/revendeur/", {"action": "preparer_les_versements", "_selected_action": [self.revendeur.pk]})

        self.assertEqual(Versement.objects.filter(statut=StatutVersement.PREPARE).count(), 1)
