"""Candidature de revendeur : brouillon, vérification SMS du numéro, envoi, étude par l'équipe."""
from datetime import timedelta
from unittest.mock import patch

from django.test import Client
from django.utils import timezone
from rest_framework.test import APIClient

from users.models import OTPCode, User
from users.phone import to_e164

from .candidatures import (
    CandidatureInvalide,
    accepter_candidature,
    demander_complement,
    refuser_candidature,
)
from .models import (
    CHARTE_VERSION,
    CandidatureRevendeur,
    Revendeur,
    StatutCandidature,
    StatutRevendeur,
    TypeRevendeur,
)
from .tests import _Base, _revendeur

NUMERO = "699222333"
URL = "/revendeurs/candidature/"


class _CandidatureBase(_Base):
    def setUp(self):
        super().setUp()
        self.api = APIClient()
        self.candidat = User.objects.create_user(phone_number="677950001", password="x", full_name="Paul Mbarga")
        self.api.force_authenticate(self.candidat)

    def _brouillon(self, **extra):
        donnees = {
            "type": "REPETITEUR", "nom_affiche": "Paul Mbarga Cours", "ville": "Douala",
            "presentation": "Je donne des cours à domicile à 20 élèves de Terminale.",
            "operateur_versement": "ORANGE", "numero_versement": NUMERO, **extra,
        }
        return self.api.put(URL, donnees, format="json")

    def _verifier(self):
        """Envoie le code SMS puis le saisit, comme le fait le candidat."""
        self.api.post(URL + "envoyer-code/")
        code = OTPCode.objects.filter(destination=to_e164(NUMERO)).latest("created_at").code
        return self.api.post(URL + "verifier-numero/", {"code": code}, format="json")

    def _soumise(self, **extra):
        self._brouillon(**extra)
        self._verifier()
        reponse = self.api.post(URL + "soumettre/", {"charte_version": CHARTE_VERSION, "accepte": True}, format="json")
        assert reponse.status_code == 200, reponse.content
        return CandidatureRevendeur.objects.get(user=self.candidat)


class BrouillonTests(_CandidatureBase):
    def test_etat_initial(self):
        data = self.api.get(URL).json()

        self.assertEqual((data["candidature"], data["peut_candidater"], data["raison"]), (None, True, None))
        self.assertEqual(data["charte_version"], CHARTE_VERSION)

    def test_exige_la_connexion(self):
        self.assertEqual(APIClient().get(URL).status_code, 401)

    def test_enregistre_un_brouillon_puis_le_complete(self):
        self.assertEqual(self._brouillon().status_code, 200)
        reponse = self.api.put(URL, {"ville": "Yaoundé"}, format="json").json()

        self.assertEqual((reponse["statut"], reponse["ville"], reponse["nom_affiche"]), ("BROUILLON", "Yaoundé", "Paul Mbarga Cours"))
        self.assertEqual(CandidatureRevendeur.objects.count(), 1)

    def test_numero_ramene_au_format_local(self):
        reponse = self._brouillon(numero_versement="+237 699 222 333").json()
        self.assertEqual(reponse["numero_versement"], NUMERO)

    def test_numero_invalide_refuse(self):
        self.assertEqual(self._brouillon(numero_versement="12345").status_code, 400)

    def test_type_inconnu_refuse(self):
        self.assertEqual(self._brouillon(type="PIRATE").status_code, 400)

    def test_un_revendeur_ne_peut_pas_candidater(self):
        revendeur = _revendeur(tel="677950002", code="DEJA77")
        self.api.force_authenticate(revendeur.user)

        reponse = self._brouillon()

        self.assertEqual((reponse.status_code, reponse.json()["code"]), (400, "deja_revendeur"))
        self.assertFalse(self.api.get(URL).json()["peut_candidater"])

    def test_pas_de_candidature_depuis_une_session_enfant(self):
        with patch("revendeurs.views_candidature.exiger_mode_parent") as garde:
            from rest_framework.response import Response

            garde.return_value = Response({"code": "session_restreinte"}, status=403)
            self.assertEqual(self._brouillon().status_code, 403)

    def test_une_seule_candidature_ouverte_par_compte(self):
        self._brouillon()
        self._brouillon(ville="Garoua")

        self.assertEqual(CandidatureRevendeur.objects.filter(user=self.candidat).count(), 1)


class VerificationDuNumeroTests(_CandidatureBase):
    def test_le_bon_code_verifie_le_numero(self):
        self._brouillon()
        reponse = self._verifier().json()

        self.assertTrue(reponse["numero_verifie"])

    def test_un_mauvais_code_est_refuse(self):
        self._brouillon()
        self.api.post(URL + "envoyer-code/")

        reponse = self.api.post(URL + "verifier-numero/", {"code": "000000"}, format="json")

        self.assertEqual((reponse.status_code, reponse.json()["code"]), (400, "code_invalide"))
        self.assertFalse(CandidatureRevendeur.objects.get().numero_est_verifie)

    def test_changer_de_numero_annule_la_verification(self):
        self._brouillon()
        self._verifier()

        reponse = self.api.put(URL, {"numero_versement": "699444555"}, format="json").json()

        self.assertFalse(reponse["numero_verifie"])

    def test_renvoyer_le_meme_numero_garde_la_verification(self):
        self._brouillon()
        self._verifier()

        self.assertTrue(self.api.put(URL, {"numero_versement": NUMERO}, format="json").json()["numero_verifie"])

    def test_envoi_du_code_sans_numero(self):
        self.api.put(URL, {"nom_affiche": "X"}, format="json")

        reponse = self.api.post(URL + "envoyer-code/")

        self.assertEqual((reponse.status_code, reponse.json()["code"]), (400, "numero_manquant"))

    def test_envoi_du_code_sans_candidature(self):
        self.assertEqual(self.api.post(URL + "envoyer-code/").status_code, 400)

    def test_le_renvoi_trop_rapide_est_limite(self):
        self._brouillon()
        self.api.post(URL + "envoyer-code/")

        reponse = self.api.post(URL + "envoyer-code/")

        self.assertEqual(reponse.status_code, 429)
        self.assertIn("retry_after", reponse.json())


class SoumissionTests(_CandidatureBase):
    def _soumettre(self, **corps):
        return self.api.post(URL + "soumettre/", {"charte_version": CHARTE_VERSION, "accepte": True, **corps}, format="json")

    def test_soumission_complete(self):
        candidature = self._soumise()

        self.assertEqual(candidature.statut, StatutCandidature.SOUMISE)
        self.assertEqual(candidature.charte_version, CHARTE_VERSION)
        self.assertIsNotNone(candidature.charte_acceptee_le)
        self.assertIsNotNone(candidature.soumise_le)
        self.assertRegex(candidature.code_attribue, r"^PAULM\d\d$")

    def test_champs_manquants(self):
        self.api.put(URL, {"nom_affiche": "Paul"}, format="json")

        self.assertEqual(self._soumettre().json()["code"], "champs_manquants")

    def test_numero_non_verifie(self):
        self._brouillon()

        self.assertEqual(self._soumettre().json()["code"], "numero_non_verifie")

    def test_charte_non_acceptee_ou_mauvaise_version(self):
        self._brouillon()
        self._verifier()

        self.assertEqual(self._soumettre(accepte=False).json()["code"], "charte_non_acceptee")
        self.assertEqual(self._soumettre(charte_version="0.0").json()["code"], "charte_non_acceptee")
        self.assertEqual(CandidatureRevendeur.objects.get().statut, StatutCandidature.BROUILLON)

    def test_ecole_ou_centre_doit_decrire_son_etablissement(self):
        self._brouillon(type="ECOLE_CENTRE")
        self._verifier()
        self.assertEqual(self._soumettre().json()["code"], "champs_manquants")

        self.api.put(URL, {"etablissement": "Collège Vogt", "fonction": "Directeur"}, format="json")
        self.assertEqual(self._soumettre().status_code, 200)

    def test_une_candidature_envoyee_n_est_plus_modifiable(self):
        self._soumise()

        reponse = self.api.put(URL, {"ville": "Bafoussam"}, format="json")

        self.assertEqual((reponse.status_code, reponse.json()["code"]), (400, "non_modifiable"))

    def test_sms_de_reception(self):
        with patch("users.sms_backends.get_sms_backend") as backend:
            self._soumise()

        textes = [appel.args[1] for appel in backend.return_value.send.call_args_list]
        self.assertTrue(any("bien reçue" in t for t in textes))

    def test_sms_en_anglais_pour_un_compte_anglophone(self):
        User.objects.filter(pk=self.candidat.pk).update(langue="en")
        with patch("users.sms_backends.get_sms_backend") as backend:
            self._soumise()

        textes = [appel.args[1] for appel in backend.return_value.send.call_args_list]
        self.assertTrue(any("received your reseller application" in t for t in textes))

    def test_numero_deja_utilise_par_un_revendeur_est_signale_sans_etre_refuse(self):
        Revendeur.objects.filter(pk=self.revendeur.pk).update(numero_versement=NUMERO)

        candidature = self._soumise()

        self.assertEqual(candidature.statut, StatutCandidature.SOUMISE)
        self.assertIn("DEMO42", candidature.alertes)

    def test_les_alertes_internes_ne_sont_jamais_exposees(self):
        Revendeur.objects.filter(pk=self.revendeur.pk).update(numero_versement=NUMERO)
        self._soumise()

        corps = str(self.api.get(URL).json())

        self.assertNotIn("alertes", corps)
        self.assertNotIn("notes_internes", corps)
        self.assertNotIn("DEMO42", corps)

    def test_retirer(self):
        self._soumise()

        reponse = self.api.post(URL + "retirer/")

        self.assertEqual(reponse.json()["statut"], "RETIREE")
        self.assertTrue(self.api.get(URL).json()["peut_candidater"])

    def test_retirer_sans_candidature(self):
        self.assertEqual(self.api.post(URL + "retirer/").status_code, 400)


class EtudeParLEquipeTests(_CandidatureBase):
    def setUp(self):
        super().setUp()
        self.candidature = self._soumise()

    def test_acceptation_cree_la_fiche_et_previent_le_candidat(self):
        with patch("users.sms_backends.get_sms_backend") as backend:
            revendeur = accepter_candidature(self.candidature, self.admin)

        self.assertEqual((revendeur.user, revendeur.statut, revendeur.type), (self.candidat, StatutRevendeur.ACTIF, TypeRevendeur.REPETITEUR))
        self.assertEqual((revendeur.numero_versement, revendeur.operateur_versement), (NUMERO, "ORANGE"))
        self.assertEqual(revendeur.charte_version, CHARTE_VERSION)
        self.assertEqual(revendeur.taux_base_pct, 14)
        self.candidature.refresh_from_db()
        self.assertEqual((self.candidature.statut, self.candidature.revendeur, self.candidature.etudiee_par), (StatutCandidature.ACCEPTEE, revendeur, self.admin))
        envoye = backend.return_value.send.call_args.args[1]
        self.assertIn(revendeur.code, envoye)

    def test_apres_acceptation_le_candidat_accede_a_son_espace(self):
        accepter_candidature(self.candidature, self.admin)

        reponse = self.api.get("/revendeurs/moi/")

        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse.json()["statut"], "ACTIF")

    def test_le_code_attribue_est_modifiable_avant_l_acceptation(self):
        CandidatureRevendeur.objects.filter(pk=self.candidature.pk).update(code_attribue="paulcours")
        self.candidature.refresh_from_db()

        self.assertEqual(accepter_candidature(self.candidature, self.admin).code, "PAULCOURS")

    def test_un_commercial_recoit_son_palier(self):
        CandidatureRevendeur.objects.filter(pk=self.candidature.pk).update(type="COMMERCIAL")
        self.candidature.refresh_from_db()

        revendeur = accepter_candidature(self.candidature, self.admin)

        self.assertEqual((revendeur.palier_seuil, revendeur.palier_taux_pct), (30, 17))

    def test_un_code_deja_pris_bloque_l_acceptation_sans_rien_changer(self):
        CandidatureRevendeur.objects.filter(pk=self.candidature.pk).update(code_attribue=self.revendeur.code)
        self.candidature.refresh_from_db()

        with self.assertRaises(CandidatureInvalide) as ctx:
            accepter_candidature(self.candidature, self.admin)

        self.assertEqual(ctx.exception.code, "code_invalide")
        self.candidature.refresh_from_db()
        self.assertEqual(self.candidature.statut, StatutCandidature.SOUMISE)
        self.assertFalse(Revendeur.objects.filter(user=self.candidat).exists())

    def test_un_code_egal_a_un_code_de_parrainage_est_refuse(self):
        CandidatureRevendeur.objects.filter(pk=self.candidature.pk).update(code_attribue=self.admin.referral_code)
        self.candidature.refresh_from_db()

        with self.assertRaises(CandidatureInvalide):
            accepter_candidature(self.candidature, self.admin)

    def test_deuxieme_acceptation_refusee(self):
        accepter_candidature(self.candidature, self.admin)

        with self.assertRaises(CandidatureInvalide) as ctx:
            accepter_candidature(self.candidature, self.admin)

        self.assertEqual(ctx.exception.code, "deja_traitee")
        self.assertEqual(Revendeur.objects.filter(user=self.candidat).count(), 1)

    def test_refus_exige_un_motif_puis_le_montre_au_candidat(self):
        with self.assertRaises(CandidatureInvalide) as ctx:
            refuser_candidature(self.candidature, self.admin)
        self.assertEqual(ctx.exception.code, "motif_obligatoire")

        CandidatureRevendeur.objects.filter(pk=self.candidature.pk).update(motif="Zone déjà couverte")
        self.candidature.refresh_from_db()
        with patch("users.sms_backends.get_sms_backend") as backend:
            refuser_candidature(self.candidature, self.admin)

        data = self.api.get(URL).json()
        self.assertEqual((data["candidature"]["statut"], data["candidature"]["motif"]), ("REFUSEE", "Zone déjà couverte"))
        self.assertIn("pas été retenue", backend.return_value.send.call_args.args[1])

    def test_apres_un_refus_pas_de_nouvelle_candidature_avant_30_jours(self):
        CandidatureRevendeur.objects.filter(pk=self.candidature.pk).update(motif="Non")
        self.candidature.refresh_from_db()
        refuser_candidature(self.candidature, self.admin)

        data = self.api.get(URL).json()
        self.assertEqual((data["peut_candidater"], data["raison"]), (False, "refus_recent"))
        self.assertIsNotNone(data["reouverture_le"])
        self.assertEqual(self._brouillon().json()["code"], "refus_recent")

        CandidatureRevendeur.objects.filter(pk=self.candidature.pk).update(etudiee_le=timezone.now() - timedelta(days=31))
        self.assertTrue(self.api.get(URL).json()["peut_candidater"])
        self.assertEqual(self._brouillon().status_code, 200)

    def test_complement_demande_puis_renvoi(self):
        CandidatureRevendeur.objects.filter(pk=self.candidature.pk).update(motif="Précise tes zones de vente")
        self.candidature.refresh_from_db()
        demander_complement(self.candidature, self.admin)

        data = self.api.get(URL).json()["candidature"]
        self.assertEqual((data["statut"], data["motif"]), ("A_COMPLETER", "Précise tes zones de vente"))

        self.api.put(URL, {"presentation": "Je vends dans les quartiers Bonabéri et Akwa."}, format="json")
        renvoi = self.api.post(URL + "soumettre/", {"charte_version": CHARTE_VERSION, "accepte": True}, format="json")

        self.assertEqual(renvoi.status_code, 200)
        self.assertEqual(renvoi.json()["statut"], "SOUMISE")
        self.assertEqual(renvoi.json()["motif"], "")

    def test_complement_avec_un_nouveau_numero_exige_une_nouvelle_verification(self):
        CandidatureRevendeur.objects.filter(pk=self.candidature.pk).update(motif="Autre numéro ?")
        self.candidature.refresh_from_db()
        demander_complement(self.candidature, self.admin)

        self.api.put(URL, {"numero_versement": "699777888"}, format="json")
        renvoi = self.api.post(URL + "soumettre/", {"charte_version": CHARTE_VERSION, "accepte": True}, format="json")

        self.assertEqual(renvoi.json()["code"], "numero_non_verifie")

    def test_le_motif_d_une_candidature_acceptee_n_est_pas_montre(self):
        CandidatureRevendeur.objects.filter(pk=self.candidature.pk).update(motif="note interne")
        self.candidature.refresh_from_db()
        accepter_candidature(self.candidature, self.admin)

        data = self.api.get(URL).json()["candidature"]

        self.assertEqual((data["statut"], data["motif"]), ("ACCEPTEE", ""))
        self.assertTrue(data["code"])

    def test_un_candidat_ne_voit_pas_la_candidature_d_un_autre(self):
        autre = User.objects.create_user(phone_number="677950009", password="x")
        self.api.force_authenticate(autre)

        data = self.api.get(URL).json()

        self.assertIsNone(data["candidature"])
        self.assertTrue(data["peut_candidater"])


class AdminCandidatureTests(_CandidatureBase):
    def setUp(self):
        super().setUp()
        self.candidature = self._soumise()
        self.web = Client()
        self.web.force_login(User.objects.create_superuser(phone_number="677950099", password="x"))

    def test_pages_sans_erreur(self):
        self.assertEqual(self.web.get("/admin/revendeurs/candidaturerevendeur/").status_code, 200)
        self.assertEqual(self.web.get(f"/admin/revendeurs/candidaturerevendeur/{self.candidature.pk}/change/").status_code, 200)

    def test_action_accepter(self):
        self.web.post("/admin/revendeurs/candidaturerevendeur/", {"action": "accepter", "_selected_action": [self.candidature.pk]})

        self.candidature.refresh_from_db()
        self.assertEqual(self.candidature.statut, StatutCandidature.ACCEPTEE)
        self.assertTrue(Revendeur.objects.filter(user=self.candidat, statut=StatutRevendeur.ACTIF).exists())

    def test_action_refuser_sans_motif_ne_change_rien(self):
        self.web.post("/admin/revendeurs/candidaturerevendeur/", {"action": "refuser", "_selected_action": [self.candidature.pk]})

        self.candidature.refresh_from_db()
        self.assertEqual(self.candidature.statut, StatutCandidature.SOUMISE)

    def test_action_refuser_avec_motif(self):
        CandidatureRevendeur.objects.filter(pk=self.candidature.pk).update(motif="Dossier incomplet")

        self.web.post("/admin/revendeurs/candidaturerevendeur/", {"action": "refuser", "_selected_action": [self.candidature.pk]})

        self.candidature.refresh_from_db()
        self.assertEqual(self.candidature.statut, StatutCandidature.REFUSEE)
