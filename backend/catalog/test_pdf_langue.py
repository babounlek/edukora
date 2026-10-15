"""Les PDF du GCE sont en anglais de bout en bout (voir catalog.pdf_textes) : sujet d'épreuve, fiche d'exercices,
fiche de quiz, épreuve inédite. Le rendu Playwright reste hors tests : on vérifie le HTML produit par Django."""
import re
from types import SimpleNamespace

from django.test import SimpleTestCase, TestCase

from fiches.models import FicheGeneree, FicheItem
from fiches.pdf import _combined_markdown, _render_html as _render_fiche
from inedit.models import Blueprint, EpreuveInedite
from inedit.sujet_pdf import _render_html as _render_inedite
from quiz.pdf import _resolve_cours_links, _textes as _textes_quiz
from quiz.models import CompetenceItem
from users.models import User

from .models import Country, Cursus, Examen, Lesson, LessonType, StatutContenu, Subject, Tag
from .pdf_textes import TEXTES, adapter_markdown, langue_du_contenu, nom_pays, textes_pdf
from .sujet_pdf import _render_html

# Mots français qui ne doivent JAMAIS figurer dans un PDF du GCE.
FRANCAIS = ("Sujet gratuit", "Envie de", "Scanne-moi", "FCFA par enfant", "Prêt(e)", "répétiteur", "Corrigé",
            "Durée", "Barème", "Continue à", "QR code vers", "Épreuve inédite", "réservé", "Exercice", "Cameroun",
            "points)")


class TextesTests(SimpleTestCase):
    def test_les_deux_langues_ont_les_memes_cles_et_les_memes_variables(self):
        self.assertEqual(set(TEXTES["fr"]), set(TEXTES["en"]))
        for cle, fr in TEXTES["fr"].items():
            if isinstance(fr, str):
                en = TEXTES["en"][cle]
                self.assertEqual(sorted(re.findall(r"\{\w+\}", fr)), sorted(re.findall(r"\{\w+\}", en)), cle)

    def test_langue_du_contenu_suit_la_matiere_puis_le_cursus(self):
        self.assertEqual(langue_du_contenu(subject=SimpleNamespace(langue="en")), "en")
        self.assertEqual(langue_du_contenu(subject=SimpleNamespace(langue="fr")), "fr")
        self.assertEqual(langue_du_contenu(cursus=SimpleNamespace(langue="en")), "en")
        self.assertEqual(langue_du_contenu(), "fr")

    def test_variables_remplacees_et_langue_inconnue_en_francais(self):
        self.assertIn("EduKora", textes_pdf("en", site="EduKora")["sujet_cta_corps"])
        self.assertEqual(textes_pdf("klingon")["langue"], "fr")


class AdapterMarkdownTests(SimpleTestCase):
    def test_reperes_francais_du_gce_reecrits_en_anglais(self):
        texte = "**Exercice 3 (6 points)**\n\nDefine work. *[2 pts]*\n\n### Rappel de méthode\n\nUse F.d\n\n### Corrigé\n\nW = Fd"
        rendu = adapter_markdown(texte, "en")
        self.assertIn("**Exercise 3 (6 marks)**", rendu)
        self.assertIn("*[2 marks]*", rendu)
        self.assertIn("### Method reminder", rendu)
        self.assertIn("### Solution", rendu)
        self.assertNotIn("Exercice", rendu)

    def test_un_point_au_singulier_et_virgule_decimale(self):
        self.assertIn("(1 mark)", adapter_markdown("**Exercice 1 (1 point)**", "en"))
        self.assertIn("(2,5 marks)", adapter_markdown("**Exercice 1 (2,5 pts)**", "en"))

    def test_contenu_anglais_et_francais_epargnes(self):
        anglais = "**Question 1 (6 marks)**\n\nThe point of application of the force."
        self.assertEqual(adapter_markdown(anglais, "en"), anglais)
        francais = "**Exercice 3 (6 points)**\n\n### Rappel de méthode"
        self.assertEqual(adapter_markdown(francais, "fr"), francais)

    def test_nom_du_pays_dans_la_langue_du_pdf(self):
        self.assertEqual(nom_pays("CM", "Cameroun", "en"), "Cameroon")
        self.assertEqual(nom_pays("cm", "Cameroun", "fr"), "Cameroun")
        self.assertEqual(nom_pays("XX", "Pays inconnu", "en"), "Pays inconnu")


class _Base(TestCase):
    @classmethod
    def setUpTestData(cls):
        cm = Country.objects.get_or_create(code="CM", defaults={"label": "Cameroun"})[0]
        cls.cm = cm
        cls.cursus_al = Cursus.objects.get_or_create(country=cm, examen=Examen.GCE_AL, series=None)[0]
        cls.matiere_gce = Subject.objects.create(country=cm, code="GCE_PHYSICS_P", label="Physics", langue="en")
        cls.matiere_fr = Subject.objects.get(country__code="CM", code="MATHS")
        cls.cursus_bac = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")

    def assertSansFrancais(self, html):
        # Le texte VISIBLE : les commentaires de la feuille de style et du script ne sont pas imprimés.
        visible = re.sub(r"<(style|script)\b.*?</\1>", "", html, flags=re.S)
        for mot in FRANCAIS:
            self.assertNotIn(mot, visible, mot)


class SujetPdfLangueTests(_Base):
    def _lesson(self, subject, cursus, titre):
        lesson = Lesson.objects.create(
            title=titre, subject=subject, lesson_type=LessonType.CORR, year=2023, duree_epreuve="2 hours",
            statut=StatutContenu.VALIDE, content_markdown="**Exercice 1 (6 points)**\n\nDefine work.",
        )
        lesson.cursus.add(cursus)
        return lesson

    def test_sujet_du_gce_en_anglais(self):
        html = _render_html(self._lesson(self.matiere_gce, self.cursus_al, "Physics GCE A Level - Paper 2"))
        self.assertIn('<html lang="en">', html)
        for attendu in ("Free paper", "Want to check your answers?", "15,000 FCFA per child", "View the correction",
                        "QR code to the correction", "Scan me", "Free-access paper", "Duration: 2 hours",
                        "Session 2023", "Cameroon", "Exercise 1 (6 marks)"):
            self.assertIn(attendu, html)
        self.assertSansFrancais(html)

    def test_sujet_francophone_inchange(self):
        html = _render_html(self._lesson(self.matiere_fr, self.cursus_bac, "Mathématiques BAC C 2023"))
        self.assertIn('<html lang="fr">', html)
        for attendu in ("Sujet gratuit", "Envie de vérifier tes réponses ?", "15 000 FCFA par enfant", "Scanne-moi",
                        "Durée : 2 hours"):
            self.assertIn(attendu, html)

    def test_origine_non_officielle_traduite(self):
        lesson = self._lesson(self.matiere_gce, self.cursus_al, "Physics mock")
        lesson.origine = "BLANC"
        lesson.save(update_fields=["origine"])
        self.assertIn("Mock exam", _render_html(lesson))


class FichePdfLangueTests(_Base):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677300777", password="x", full_name="Mr Tabi")
        self.theme = Tag.objects.create(name="work energy")
        self.fiche = FicheGeneree.objects.create(
            owner=self.user, cursus=self.cursus_al, subject=self.matiere_gce, titre="Worksheet", nombre_questions=1,
        )
        item = CompetenceItem.objects.create(
            external_id="x-1", theme=self.theme, subject=self.matiere_gce, enonce_markdown="Define work.",
            corrige_markdown="Work is force times distance.", statut=StatutContenu.VALIDE,
        )
        item.cursus.add(self.cursus_al)
        FicheItem.objects.create(fiche=self.fiche, competence_item=item, ordre=1)

    def test_fiche_du_gce_en_anglais(self):
        for corrige, template, attendu in (
            (False, "fiches/fiche_sujet_pdf_template.html", "Exercise sheet"),
            (True, "fiches/fiche_corrige_pdf_template.html", "Solutions (tutor's copy)"),
        ):
            html = _render_fiche(self.fiche, avec_corrige=corrige, template_name=template, deep_link="https://x/y")
            self.assertIn('<html lang="en">', html)
            self.assertIn(attendu.replace("'", "&#x27;"), html)
            self.assertIn("Mr Tabi", html)
            self.assertSansFrancais(html)

    def test_titre_de_section_du_corrige_en_anglais(self):
        self.assertIn("### Solution", _combined_markdown(self.fiche, avec_corrige=True))
        self.assertNotIn("Corrigé", _combined_markdown(self.fiche, avec_corrige=True))

    def test_repetiteur_sans_nom_est_traduit(self):
        self.user.full_name = ""
        self.user.save(update_fields=["full_name"])
        html = _render_fiche(self.fiche, avec_corrige=False, template_name="fiches/fiche_sujet_pdf_template.html", deep_link="https://x/y")
        self.assertIn("a tutor", html)

    def test_fiche_francophone_inchangee(self):
        fiche = FicheGeneree.objects.create(
            owner=self.user, cursus=self.cursus_bac, subject=self.matiere_fr, titre="Ma fiche", nombre_questions=0,
        )
        html = _render_fiche(fiche, avec_corrige=False, template_name="fiches/fiche_sujet_pdf_template.html", deep_link="https://x/y")
        self.assertIn('<html lang="fr">', html)
        self.assertIn("Fiche d&#x27;exercices", html)


class QuizPdfLangueTests(_Base):
    def test_textes_du_quiz_dans_la_langue_du_contenu(self):
        gce = SimpleNamespace(subject_id=1, subject=self.matiere_gce, cursus=self.cursus_al)
        fr = SimpleNamespace(subject_id=2, subject=self.matiere_fr, cursus=self.cursus_bac)
        self.assertEqual(_textes_quiz(gce)["quiz_brand"], "Quiz sheet")
        self.assertEqual(_textes_quiz(fr)["quiz_brand"], "Fiche de quiz")

    def test_session_sans_matiere_suit_le_cursus(self):
        sans_matiere = SimpleNamespace(subject_id=None, subject=None, cursus=self.cursus_al)
        self.assertEqual(_textes_quiz(sans_matiere)["quiz_brand"], "Quiz sheet")

    def test_lien_vers_le_cours_traduit(self):
        tx = textes_pdf("en")
        rendu = _resolve_cours_links("[COURS_LINK:vectors]", tx["voir_cours"])
        self.assertIn("[View the full lesson →]", rendu)
        self.assertIn("/cours/vectors", rendu)
        self.assertIn("[Voir le cours complet →]", _resolve_cours_links("[COURS_LINK:vectors]"))


class InedPdfLangueTests(_Base):
    def test_inedite_du_gce_en_anglais(self):
        blueprint = Blueprint.objects.create(
            subject=self.matiere_gce, titre="BP", statut=StatutContenu.VALIDE, duree_minutes=90, bareme_total=60,
        )
        blueprint.cursus.set([self.cursus_al])
        epreuve = EpreuveInedite.objects.create(
            blueprint=blueprint, subject=self.matiere_gce, titre="Original paper", statut=StatutContenu.VALIDE,
            enonce_markdown="Define work.",
        )
        epreuve.cursus.set([self.cursus_al])
        html = _render_inedite(epreuve)
        self.assertIn('<html lang="en">', html)
        for attendu in ("Paper - Original practice paper", "Ready to sit the paper?", "Duration: 90 min", "Marks: 60"):
            self.assertIn(attendu, html)
        self.assertSansFrancais(html)


class GenererPdfParLangueTests(_Base):
    """`generate_sujet_pdfs --langue en --force` régénère les PDF du GCE seulement (après un changement de gabarit)."""

    def test_langue_en_ne_traite_que_les_matieres_anglophones(self):
        from io import StringIO
        from unittest.mock import patch

        from django.core.management import call_command

        gce = Lesson.objects.create(
            title="Physics GCE", subject=self.matiere_gce, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        fr = Lesson.objects.create(
            title="Maths BAC", subject=self.matiere_fr, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        for lesson in (gce, fr):
            Lesson.objects.filter(pk=lesson.pk).update(sujet_pdf="cm/deja-sujet.pdf")
        with patch("catalog.management.commands.generate_sujet_pdfs.save_sujet_pdf") as sauver:
            call_command("generate_sujet_pdfs", "--langue", "en", "--force", stdout=StringIO())
        traites = [appel.args[0].pk for appel in sauver.call_args_list]
        self.assertEqual(traites, [gce.pk])
