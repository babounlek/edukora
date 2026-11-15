"""Le bloc de fin et le QR d'en-tête communs à tous les PDF (voir catalog.pdf_fin). Le rendu Playwright reste hors
tests : on vérifie la règle de choix de la taille, le contexte, et le HTML produit par Django pour chaque type."""
import re

from django.test import SimpleTestCase

from fiches.models import FicheGeneree
from fiches.pdf import _render_html as _render_fiche
from inedit.models import Blueprint, EpreuveInedite
from inedit.sujet_pdf import _render_html as _render_inedite
from users.models import User

from .models import Lesson, LessonType, StatutContenu, Subject
from .pdf_fin import (
    BANDEAU,
    DEMI,
    MINI,
    PLEINE,
    SANS_BLOC,
    avec_position,
    compter_pages,
    contexte_fin,
    imprimer_a_la_bonne_taille,
)
from .pdf_textes import textes_pdf
from .sujet_pdf import MAX_AUTRES_SESSIONS, _footer_template, _render_html
from .test_pdf_langue import _Base


def _pdf(pages):
    """Des octets qui ont, pour compter_pages, la forme d'un PDF de Chromium de `pages` pages."""
    return b"%PDF-1.4\n<</Type /Pages /Count 9>>\n" + b"<</Type /Page\n/Parent 2 0 R>>\n" * pages


class CompterPagesTests(SimpleTestCase):
    def test_compte_les_pages_et_ignore_l_arbre_des_pages(self):
        self.assertEqual(compter_pages(_pdf(4)), 4)
        self.assertEqual(compter_pages(b"<</Type/Page>><</Type/Pages>>"), 1)

    def test_un_fichier_illisible_compte_zero(self):
        self.assertEqual(compter_pages(b"pas un pdf"), 0)


class ChoixDeLaTailleTests(SimpleTestCase):
    """La plus grande taille qui n'ajoute pas de page au contenu ; à défaut, la pleine sur la page de plus."""

    def _choisir(self, pages_par_taille):
        essais = []

        def imprimer(taille):
            essais.append(taille)
            return _pdf(pages_par_taille[taille]) + taille.encode()

        return imprimer_a_la_bonne_taille(imprimer), essais

    def test_garde_la_plus_grande_taille_qui_tient(self):
        pdf, essais = self._choisir({SANS_BLOC: 3, PLEINE: 4, DEMI: 3, BANDEAU: 3, MINI: 3})
        self.assertTrue(pdf.endswith(b"demi"))
        self.assertEqual(essais, [SANS_BLOC, PLEINE, DEMI])

    def test_la_pleine_quand_la_derniere_page_est_presque_vide(self):
        pdf, _ = self._choisir({SANS_BLOC: 3, PLEINE: 3, DEMI: 3, BANDEAU: 3, MINI: 3})
        self.assertTrue(pdf.endswith(b"pleine"))

    def test_la_mini_plutot_qu_une_page_de_plus(self):
        pdf, _ = self._choisir({SANS_BLOC: 3, PLEINE: 4, DEMI: 4, BANDEAU: 4, MINI: 3})
        self.assertTrue(pdf.endswith(b"mini"))

    def test_si_rien_ne_tient_la_page_de_plus_recoit_la_pleine(self):
        pdf, essais = self._choisir({SANS_BLOC: 3, PLEINE: 4, DEMI: 4, BANDEAU: 4, MINI: 4})
        self.assertTrue(pdf.endswith(b"pleine"))
        self.assertEqual(compter_pages(pdf), 4)
        self.assertEqual(essais, [SANS_BLOC, PLEINE, DEMI, BANDEAU, MINI, PLEINE])

    def test_compte_illisible_on_garde_le_bandeau(self):
        self.assertEqual(imprimer_a_la_bonne_taille(lambda taille: taille.encode()), b"bandeau")


class ContexteFinTests(SimpleTestCase):
    def _fin(self, **options):
        tx = textes_pdf("fr", site="EduKora")
        return contexte_fin(
            tx, lien="https://edukora.africa/cm/epreuves/x?ref=pdf_sujet", titre="T", corps="C", bouton="B",
            qr_alt="QR", legende="L", **options,
        )

    def test_la_position_s_ajoute_a_l_adresse(self):
        self.assertEqual(avec_position("https://x/y?ref=pdf", "p1"), "https://x/y?ref=pdf&pos=p1")
        self.assertEqual(avec_position("https://x/y", "fin"), "https://x/y?pos=fin")

    def test_le_qr_de_l_entete_et_celui_de_la_fin_se_distinguent(self):
        fin = self._fin()
        self.assertTrue(fin["lien"].endswith("?ref=pdf_sujet&pos=fin"))
        self.assertTrue(fin["entete"]["lien"].endswith("?ref=pdf_sujet&pos=p1"))
        self.assertNotEqual(fin["qr"], fin["entete"]["qr"])
        self.assertTrue(fin["qr"].startswith("data:image/png;base64,"))

    def test_la_ligne_parents_n_apparait_que_sur_demande(self):
        self.assertEqual(self._fin()["parents"], "")
        self.assertIn("Mobile Money", self._fin(parents=True)["parents"])

    def test_sans_appareil_photo_on_dit_quoi_chercher_ou_quelle_adresse_taper(self):
        with self.settings(PDF_SITE_URL="https://edukora.africa"):
            self.assertIn("cherche « Maths BAC C 2023 »", self._fin(recherche="Maths BAC C 2023")["sans_appareil"])
            self.assertIn("Ouvre edukora.africa et", self._fin(recherche="Maths")["sans_appareil"])
            self.assertIn("Ouvre edukora.africa/cm.", self._fin(adresse="edukora.africa/cm")["sans_appareil"])
            self.assertIn("Ouvre edukora.africa.", self._fin()["sans_appareil"])

    def test_aucun_montant_dans_les_textes_du_bloc(self):
        for langue in ("fr", "en"):
            tx = textes_pdf(langue, site="EduKora")
            texte = " ".join([tx["fin_parents"], tx["fin_aussi_titre"], *tx["fin_aussi"]])
            self.assertNotRegex(texte, r"\d", langue)

    def test_le_pied_de_chaque_page_porte_l_adresse_du_site(self):
        with self.settings(PDF_SITE_URL="https://edukora.africa", SITE_NAME="EduKora"):
            self.assertIn("EduKora - edukora.africa - ", _footer_template())


class BlocDeFinDuSujetTests(_Base):
    def _lesson(self, titre, annee, subject=None, **champs):
        lesson = Lesson.objects.create(
            title=titre, subject=subject or self.matiere_fr, lesson_type=LessonType.CORR, year=annee,
            statut=champs.pop("statut", StatutContenu.VALIDE), content_markdown="**Exercice 1**\n\nCalculer.", **champs,
        )
        lesson.cursus.add(self.cursus_bac)
        return lesson

    def _autres(self, html):
        bloc = re.search(r'<div class="fin-autres">.*?</div>', html, flags=re.S)
        return re.findall(r'<a href="([^"]+)">(\d{4})</a>', bloc.group(0)) if bloc else []

    def test_le_bloc_et_le_qr_d_entete_sont_dans_le_sujet(self):
        html = _render_html(self._lesson("Mathématiques BAC C 2023", 2023))
        self.assertIn('class="fin-ensemble"', html)
        self.assertIn('class="entete-qr"', html)
        self.assertIn("La correction", html)
        self.assertIn("pos=p1", html)
        self.assertIn("pos=fin", html)
        self.assertIn("cherche « Mathématiques BAC C 2023 »", html)
        self.assertIn("Parents :", html)
        self.assertIn("Les anciennes épreuves, corrigées pas à pas", html)

    def test_les_autres_sessions_de_la_meme_epreuve_les_plus_recentes_d_abord(self):
        lesson = self._lesson("Mathématiques BAC C 2023", 2023)
        self._lesson("Mathématiques BAC C 2021", 2021)
        self._lesson("Mathématiques BAC C 2024", 2024)
        autres = self._autres(_render_html(lesson))
        self.assertEqual([annee for _, annee in autres], ["2024", "2021"])
        self.assertIn("/cm/epreuves/mathematiques-bac-c-2024?ref=pdf_sujet&amp;pos=autres", autres[0][0])

    def test_ni_brouillon_ni_autre_matiere_ni_examen_blanc_ni_la_meme_annee(self):
        lesson = self._lesson("Mathématiques BAC C 2023", 2023)
        self._lesson("Mathématiques BAC C 2022 brouillon", 2022, statut=StatutContenu.BROUILLON)
        self._lesson("Mathématiques BAC C 2020 blanc", 2020, origine="BLANC")
        self._lesson("Mathématiques BAC C 2023 sujet 2", 2023)
        autre_matiere = Subject.objects.filter(country=self.cm).exclude(pk=self.matiere_fr.pk).first()
        self._lesson("Autre matière 2019", 2019, subject=autre_matiere)
        self.assertEqual(self._autres(_render_html(lesson)), [])

    def test_une_seule_epreuve_par_annee_et_un_nombre_borne(self):
        lesson = self._lesson("Mathématiques BAC C 2023", 2023)
        for annee in range(2000, 2000 + MAX_AUTRES_SESSIONS + 3):
            self._lesson(f"Mathématiques BAC C {annee}", annee)
        self._lesson("Mathématiques BAC C 2010 bis", 2010)
        annees = [annee for _, annee in self._autres(_render_html(lesson))]
        self.assertEqual(len(annees), MAX_AUTRES_SESSIONS)
        self.assertEqual(len(set(annees)), MAX_AUTRES_SESSIONS)

    def test_une_epreuve_sans_annee_ne_liste_rien(self):
        self._lesson("Mathématiques BAC C 2024", 2024)
        self.assertEqual(self._autres(_render_html(self._lesson("Mathématiques BAC C", None))), [])

    def test_le_sujet_du_gce_garde_son_bloc_en_anglais(self):
        lesson = Lesson.objects.create(
            title="Physics GCE A Level 2023", subject=self.matiere_gce, lesson_type=LessonType.CORR, year=2023,
            statut=StatutContenu.VALIDE, content_markdown="Define work.",
        )
        lesson.cursus.add(self.cursus_al)
        html = _render_html(lesson)
        for attendu in ("On EduKora you will also find", "No camera?", "Parents: the subscription", "The correction"):
            self.assertIn(attendu, html)
        self.assertSansFrancais(html)


class BlocDeFinDesAutresPdfTests(_Base):
    """Fiches et inédites partagent le même bloc ; la ligne pour les parents ne va que sur ce qui circule."""

    def setUp(self):
        self.user = User.objects.create_user(phone_number="677300778", password="x", full_name="Mme Ngo")
        self.fiche = FicheGeneree.objects.create(
            owner=self.user, cursus=self.cursus_bac, subject=self.matiere_fr, titre="Ma fiche", nombre_questions=0,
        )

    def _fiche(self, corrige):
        gabarit = "fiches/fiche_corrige_pdf_template.html" if corrige else "fiches/fiche_sujet_pdf_template.html"
        return _render_fiche(
            self.fiche, avec_corrige=corrige, template_name=gabarit, deep_link="https://edukora.africa/x?ref=pdf_fiche",
        )

    def test_la_fiche_distribuee_aux_eleves_parle_aux_parents(self):
        html = self._fiche(corrige=False)
        self.assertIn('class="fin-ensemble"', html)
        self.assertIn('class="entete-qr"', html)
        self.assertIn("Parents :", html)
        self.assertIn("Fiche préparée par Mme Ngo", html)
        self.assertIn("/cm.", html)

    def test_le_corrige_du_repetiteur_renvoie_a_l_outil_sans_ligne_parents(self):
        html = self._fiche(corrige=True)
        self.assertIn("Créer une fiche", html)
        self.assertIn("/fiches.", html)
        self.assertNotIn("Parents :", html)

    def test_l_inedite_reservee_aux_abonnes_n_a_pas_de_ligne_parents(self):
        blueprint = Blueprint.objects.create(
            subject=self.matiere_fr, titre="BP", statut=StatutContenu.VALIDE, duree_minutes=90, bareme_total=20,
        )
        blueprint.cursus.set([self.cursus_bac])
        epreuve = EpreuveInedite.objects.create(
            blueprint=blueprint, subject=self.matiere_fr, titre="Maths BAC C - Épreuve inédite n°1",
            statut=StatutContenu.VALIDE, enonce_markdown="Calculer.",
        )
        epreuve.cursus.set([self.cursus_bac])
        html = _render_inedite(epreuve)
        self.assertIn('class="fin-ensemble"', html)
        self.assertIn('class="entete-qr"', html)
        self.assertIn("Passer l&#x27;épreuve", html)
        self.assertIn("pos=fin", html)
        self.assertNotIn("Parents :", html)
