"""Pages sans identifiant servies aux moteurs et aux robots de partage (voir catalog.pages_statiques) : un titre propre,
un texte et des liens vers les pages d'examen au lieu du HTML vide de la SPA."""
import re

from django.conf import settings
from django.test import TestCase

from aide.models import ArticleAide, CategorieAide

from .apercu_partage import infos_page
from .models import Country, Cursus, Examen, Lesson, LessonType, StatutContenu, Subject


class PagesStatiquesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        pays, _ = Country.objects.get_or_create(
            code="CM", defaults={"label": "Cameroun", "dial_code": "+237", "currency": "XAF"},
        )
        cls.base = settings.FRONTEND_URL
        cls.bepc, _ = Cursus.objects.get_or_create(country=pays, examen=Examen.BEPC, series=None)
        cls.gce, _ = Cursus.objects.get_or_create(country=pays, examen=Examen.GCE_OL, series=None)
        maths = Subject.objects.create(country=pays, code="PST_MATHS", label="Mathématiques", langue="fr")
        anglais = Subject.objects.create(country=pays, code="PST_GCE", label="Mathematics", langue="en")
        for titre, sujet, annee, cursus in (
            ("Maths BEPC 2026", maths, 2026, cls.bepc), ("Maths BEPC 2025", maths, 2025, cls.bepc),
            ("Maths BEPC 2024", maths, 2024, cls.bepc), ("Mathematics GCE O Level 2019", anglais, 2019, cls.gce),
        ):
            lesson = Lesson.objects.create(
                title=titre, subject=sujet, lesson_type=LessonType.CORR, year=annee, statut=StatutContenu.VALIDE,
            )
            lesson.cursus.add(cursus)
        cls.article = ArticleAide.objects.create(
            slug="comment-payer", categorie=CategorieAide.choices[0][0], titre_fr="Comment payer ?",
            resume_fr="Les moyens de paiement.", corps_fr="Par mobile money.",
        )

    def get(self, chemin):
        return self.client.get(f"/prerendu/{chemin}")

    def _titre(self, html):
        return re.search(r"<title>([^<]*)</title>", html).group(1)

    def _canonical(self, html):
        return re.search(r'<link rel="canonical" href="([^"]+)">', html).group(1)

    def test_accueil_du_pays_titre_texte_et_liens_vers_les_examens(self):
        reponse = self.get("cm")
        self.assertEqual(reponse.status_code, 200)
        html = reponse.content.decode()
        self.assertEqual(self._titre(html), "Corrigés BEPC - Cameroun | EduKora")
        self.assertEqual(self._canonical(html), f"{self.base}/cm")
        # Un lien vers la page de chaque examen francophone, jamais vers le GCE (autre langue).
        self.assertIn('href="/cm/examens/bepc"', html)
        self.assertNotIn("gce", html)
        self.assertIn("3 épreuves", html)
        self.assertIn('href="/cm/epreuves"', html)

    def test_l_accueil_sans_pays_vaut_celui_du_pays_par_defaut(self):
        html = self.get("").content.decode()
        self.assertEqual(self._canonical(html), f"{self.base}/cm")

    def test_accueil_anglais_ne_liste_que_le_gce(self):
        html = self.get("en/cm").content.decode()
        self.assertIn('<html lang="en">', html)
        self.assertEqual(self._canonical(html), f"{self.base}/en/cm")
        self.assertIn('href="/en/cm/exams/gce-o-level"', html)
        self.assertNotIn("/examens/bepc", html)
        self.assertIn('hreflang="fr"', html)

    def test_listes_ont_leur_titre_et_pointent_les_autres(self):
        for chemin, titre, lien in (
            ("cm/epreuves", "Épreuves et corrigés - Cameroun | EduKora", 'href="/cm/cours"'),
            ("cm/cours", "Cours de révision - Cameroun | EduKora", 'href="/cm/themes-frequents"'),
            ("cm/themes-frequents", "Les thèmes qui reviennent le plus - Cameroun | EduKora", 'href="/cm/epreuves"'),
        ):
            html = self.get(chemin).content.decode()
            self.assertEqual(self._titre(html), titre, chemin)
            self.assertIn(lien, html, chemin)
            self.assertIn('href="/cm/examens/bepc"', html, chemin)

    def test_liste_anglaise_sous_ses_segments_traduits(self):
        html = self.get("en/cm/past-papers").content.decode()
        self.assertEqual(self._titre(html), "Past papers and solutions - Cameroon | EduKora")
        self.assertEqual(self._canonical(html), f"{self.base}/en/cm/past-papers")

    def test_tarifs_a_propos_et_aide(self):
        tarifs = self.get("tarifs").content.decode()
        self.assertEqual(self._titre(tarifs), "Tarifs : abonnement au mois par Mobile Money | EduKora")
        self.assertIn("Mobile Money", tarifs)
        self.assertEqual(self._titre(self.get("en/pricing").content.decode()), "Pricing: monthly subscription by Mobile Money | EduKora")
        self.assertEqual(self._titre(self.get("a-propos").content.decode()), "À propos | EduKora")
        aide = self.get("aide").content.decode()
        self.assertIn('href="/aide/comment-payer"', aide)
        self.assertIn("Comment payer ?", aide)

    def test_pays_inconnu_ou_sans_epreuve_dans_la_langue_donne_404(self):
        for chemin in ("zz", "zz/epreuves"):
            reponse = self.get(chemin)
            self.assertEqual(reponse.status_code, 404, chemin)
            self.assertIn('content="noindex"', reponse.content.decode())

    def test_apercu_de_partage_a_son_titre_et_son_adresse(self):
        infos = infos_page("tarifs")
        self.assertEqual(infos["titre"], "Tarifs : abonnement au mois par Mobile Money")
        self.assertEqual(infos["chemin"], "tarifs")
        self.assertEqual(infos_page("cm/epreuves")["chemin"], "cm/epreuves")
        self.assertEqual(infos_page("en/cm/past-papers")["chemin"], "en/cm/past-papers")
        self.assertEqual(infos_page("en/pricing")["chemin"], "en/pricing")
        self.assertIsNone(infos_page("zz/epreuves"))

    def test_une_epreuve_renvoie_vers_ses_voisines(self):
        html = self.get("cm/epreuves/maths-bepc-2026").content.decode()
        self.assertIn("<h2>Autres épreuves de Mathématiques</h2>", html)
        self.assertIn('href="/cm/epreuves/maths-bepc-2025"', html)
        self.assertIn('href="/cm/epreuves/maths-bepc-2024"', html)
        # Jamais un lien vers elle-même, ni vers une épreuve d'un autre examen.
        self.assertNotIn('href="/cm/epreuves/maths-bepc-2026"', html.split("Autres épreuves")[1])
        self.assertNotIn("mathematics-gce", html)
