"""
PDF d'un cours (voir catalog.cours_pdf, access.views.download_cours_pdf). Deux versions : le cours libre, sans les
exercices d'application payants, pour un visiteur ou un connecté sans abonnement ; le cours complet pour un abonné.
Le verrou est SERVEUR comme pour la lecture en ligne : le texte des exercices ne doit jamais arriver à un lecteur sans
abonnement, ni dans le HTML rendu pour le PDF, ni par le fichier servi.

Playwright n'est jamais lancé ici : on teste le HTML, le choix de la version, le cache et la file d'attente.
"""
import tempfile
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.test import override_settings

from catalog import cours_pdf
from catalog.cours_pdf import COMPLET, LIBRE, adapter_markdown_cours, empreinte, rendre_html

from .test_cours_libres import SECRETS, SECTIONS, _Base


def _stockages(dossier):
    stockages = dict(settings.STORAGES)
    stockages["cours_protected"] = {
        "BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": dossier},
    }
    return stockages


class RenduDuPdfTests(_Base):
    def test_la_version_libre_ne_contient_aucun_exercice(self):
        html = rendre_html(self.cours, LIBRE)

        for secret in SECRETS:
            self.assertNotIn(secret, html)
        for libre in ("ACCROCHE_LIBRE", "REGLE_LIBRE", "EXEMPLE_LIBRE", "ERREUR_LIBRE", "SYNTHESE_LIBRE"):
            self.assertIn(libre, html)

    def test_la_version_complete_contient_les_exercices_et_leurs_solutions(self):
        html = rendre_html(self.cours, COMPLET)

        for secret in SECRETS:
            self.assertIn(secret, html)

    def test_la_version_libre_annonce_les_exercices_reserves_aux_abonnes(self):
        self.assertIn("réservés aux abonnés", rendre_html(self.cours, LIBRE))
        self.assertNotIn("réservés aux abonnés de", rendre_html(self.cours, COMPLET))

    def test_un_renvoi_vers_un_autre_cours_devient_du_texte(self):
        texte = adapter_markdown_cours("- [Théorème de Thalès](COURS_REF:theoreme-de-thales)", "fr")

        self.assertEqual(texte, "- Théorème de Thalès")

    def test_les_titres_de_structure_d_un_cours_en_anglais_sont_traduits(self):
        source = (
            "## Prérequis\n\n- x\n\n## Exemple résolu\n\n**Étape 1 - Isoler**\n\n## Erreurs classiques\n\n### Erreur\n\n"
            "a\n\n### Pourquoi c'est faux\n\nb\n\n## Exercices d'application\n\n### Exercice 2 (moyen)\n\nPrérequis\n\n"
            "### Solution\n\n## Ce qu'il faut retenir"
        )

        texte = adapter_markdown_cours(source, "en")

        for attendu in (
            "## Prerequisites", "## Worked example", "**Step 1 - Isoler**", "## Common mistakes", "### Mistake",
            "### Why it is wrong", "## Practice exercises", "### Exercise 2 (medium)", "### Solution", "## What to remember",
        ):
            self.assertIn(attendu, texte)
        # Le contenu lui-même n'est jamais touché : seul un titre entier est réécrit.
        self.assertIn("\n\nPrérequis\n\n", texte)

    def test_les_titres_restent_en_francais_pour_un_cours_francophone(self):
        self.assertIn("## Prérequis", adapter_markdown_cours("## Prérequis\n\n- x", "fr"))

    def test_corriger_les_exercices_ne_change_pas_l_empreinte_de_la_version_libre(self):
        avant_libre, avant_complet = empreinte(self.cours, LIBRE), empreinte(self.cours, COMPLET)

        sections = [dict(s) for s in SECTIONS]
        sections[5] = {**sections[5], "items": [{"numero": 1, "difficulte": "facile", "enonce_markdown": "NEUF", "solution_markdown": "NEUF"}]}
        self.cours.sections_raw = sections
        self.cours.compile_from_sections()

        self.assertEqual(empreinte(self.cours, LIBRE), avant_libre)
        self.assertNotEqual(empreinte(self.cours, COMPLET), avant_complet)

    def test_corriger_le_cours_change_l_empreinte_de_la_version_libre(self):
        avant = empreinte(self.cours, LIBRE)

        sections = [dict(s) for s in SECTIONS]
        sections[0] = {"type": "accroche", "contenu_markdown": "ACCROCHE_CORRIGEE"}
        self.cours.sections_raw = sections

        self.assertNotEqual(empreinte(self.cours, LIBRE), avant)


class TelechargementTests(_Base):
    def setUp(self):
        super().setUp()
        self.dossier = tempfile.TemporaryDirectory()
        self.addCleanup(self.dossier.cleanup)
        surcharge = override_settings(STORAGES=_stockages(self.dossier.name))
        surcharge.enable()
        self.addCleanup(surcharge.disable)

    def _deposer(self, variante, contenu):
        from django.core.files.base import ContentFile

        cours_pdf.stockage().save(cours_pdf.nom_fichier(self.cours, variante), ContentFile(contenu))

    def _telecharger(self, *, connecte):
        if connecte:
            self.client.force_authenticate(user=self.user)
        return self.client.get(f"/access/cours/pdf/{self.cours.slug}/")

    def test_un_visiteur_recoit_la_version_libre(self):
        self._deposer(LIBRE, b"PDF-LIBRE")
        self._deposer(COMPLET, b"PDF-COMPLET")

        reponse = self._telecharger(connecte=False)

        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(b"".join(reponse.streaming_content), b"PDF-LIBRE")
        self.assertEqual(reponse["Content-Type"], "application/pdf")
        self.assertIn("attachment", reponse["Content-Disposition"])

    def test_un_connecte_sans_abonnement_recoit_la_version_libre(self):
        self._deposer(LIBRE, b"PDF-LIBRE")
        self._deposer(COMPLET, b"PDF-COMPLET")

        self.assertEqual(b"".join(self._telecharger(connecte=True).streaming_content), b"PDF-LIBRE")

    def test_un_abonne_du_cursus_recoit_la_version_complete(self):
        self._abonner(self.cursus_c)
        self._deposer(LIBRE, b"PDF-LIBRE")
        self._deposer(COMPLET, b"PDF-COMPLET")

        self.assertEqual(b"".join(self._telecharger(connecte=True).streaming_content), b"PDF-COMPLET")

    def test_un_abonne_d_un_autre_cursus_recoit_la_version_libre(self):
        self._abonner(self.cursus_d)
        self._deposer(LIBRE, b"PDF-LIBRE")
        self._deposer(COMPLET, b"PDF-COMPLET")

        self.assertEqual(b"".join(self._telecharger(connecte=True).streaming_content), b"PDF-LIBRE")

    def test_un_abonnement_expire_ne_donne_pas_la_version_complete(self):
        self._abonner(self.cursus_c, jours=-1)
        self._deposer(COMPLET, b"PDF-COMPLET")

        with mock.patch.object(cours_pdf, "mettre_en_file", return_value=cours_pdf.EN_PREPARATION) as file:
            reponse = self._telecharger(connecte=True)

        self.assertEqual(reponse.status_code, 202)
        file.assert_called_once_with(mock.ANY, LIBRE)

    def test_pas_encore_prepare_lance_la_generation_et_repond_202(self):
        with mock.patch.object(cours_pdf, "mettre_en_file", return_value=cours_pdf.EN_PREPARATION) as file:
            reponse = self._telecharger(connecte=False)

        self.assertEqual(reponse.status_code, 202)
        self.assertEqual(reponse.json(), {"statut": "en_preparation"})
        file.assert_called_once_with(mock.ANY, LIBRE)

    def test_un_abonne_declenche_la_generation_de_la_version_complete(self):
        self._abonner(self.cursus_c)

        with mock.patch.object(cours_pdf, "mettre_en_file", return_value=cours_pdf.EN_PREPARATION) as file:
            self._telecharger(connecte=True)

        file.assert_called_once_with(mock.ANY, COMPLET)

    def test_un_echec_recent_repond_503(self):
        with mock.patch.object(cours_pdf, "mettre_en_file", return_value=cours_pdf.ECHEC):
            self.assertEqual(self._telecharger(connecte=False).status_code, 503)

    def test_un_cours_inconnu_repond_404(self):
        self.assertEqual(self.client.get("/access/cours/pdf/inexistant/").status_code, 404)

    def test_un_cours_sans_contenu_libre_repond_404(self):
        self.cours.sections_raw = [SECTIONS[5]]
        self.cours.save()

        with mock.patch.object(cours_pdf, "mettre_en_file") as file:
            reponse = self._telecharger(connecte=False)

        self.assertEqual(reponse.status_code, 404)
        file.assert_not_called()

    def test_un_cours_non_publie_est_introuvable(self):
        from catalog.models import StatutContenu

        self.cours.statut = StatutContenu.BROUILLON
        self.cours.save()

        self.assertEqual(self._telecharger(connecte=False).status_code, 404)


class FileDAttenteTests(_Base):
    def setUp(self):
        super().setUp()
        self.verrous = tempfile.TemporaryDirectory()
        self.addCleanup(self.verrous.cleanup)
        patch = mock.patch.object(cours_pdf, "_dossier_verrous", return_value=Path(self.verrous.name))
        patch.start()
        self.addCleanup(patch.stop)

    def test_une_seule_generation_par_cours_meme_demandee_plusieurs_fois(self):
        with mock.patch.object(cours_pdf, "_lancer") as lancer:
            premiere = cours_pdf.mettre_en_file(self.cours, LIBRE)
            seconde = cours_pdf.mettre_en_file(self.cours, LIBRE)

        self.assertEqual((premiere, seconde), (cours_pdf.EN_PREPARATION, cours_pdf.EN_PREPARATION))
        lancer.assert_called_once()

    def test_les_deux_versions_se_generent_independamment(self):
        with mock.patch.object(cours_pdf, "_lancer") as lancer:
            cours_pdf.mettre_en_file(self.cours, LIBRE)
            cours_pdf.mettre_en_file(self.cours, COMPLET)

        self.assertEqual(lancer.call_count, 2)

    def test_au_dela_de_la_limite_on_patiente(self):
        from catalog.models import Cours, StatutContenu

        with mock.patch.object(cours_pdf, "_lancer") as lancer:
            for i in range(cours_pdf.MAX_GENERATIONS_SIMULTANEES):
                autre = Cours.objects.create(
                    external_id=f"autre-{i}", titre=f"Autre {i}", subject=self.subject, statut=StatutContenu.VALIDE,
                )
                cours_pdf.mettre_en_file(autre, LIBRE)
            statut = cours_pdf.mettre_en_file(self.cours, LIBRE)

        self.assertEqual(statut, cours_pdf.OCCUPE)
        self.assertEqual(lancer.call_count, cours_pdf.MAX_GENERATIONS_SIMULTANEES)

    def test_la_fin_d_une_generation_libere_la_place(self):
        with mock.patch.object(cours_pdf, "_lancer") as lancer:
            cours_pdf.mettre_en_file(self.cours, LIBRE)
            cours_pdf.liberer(self.cours, LIBRE)
            cours_pdf.mettre_en_file(self.cours, LIBRE)

        self.assertEqual(lancer.call_count, 2)

    def test_apres_un_echec_on_ne_relance_pas_tout_de_suite(self):
        with mock.patch.object(cours_pdf, "_lancer") as lancer:
            cours_pdf.mettre_en_file(self.cours, LIBRE)
            cours_pdf.liberer(self.cours, LIBRE, echec=True)
            statut = cours_pdf.mettre_en_file(self.cours, LIBRE)

        self.assertEqual(statut, cours_pdf.ECHEC)
        lancer.assert_called_once()

    def test_un_verrou_perime_est_ignore(self):
        import os
        import time

        with mock.patch.object(cours_pdf, "_lancer") as lancer:
            cours_pdf.mettre_en_file(self.cours, LIBRE)
            verrou = Path(self.verrous.name) / f"{LIBRE}-{self.cours.pk}.lock"
            vieux = time.time() - cours_pdf.VERROU_PERIME_S - 5
            os.utime(verrou, (vieux, vieux))
            cours_pdf.mettre_en_file(self.cours, LIBRE)

        self.assertEqual(lancer.call_count, 2)
