"""Pages prérendues pour les moteurs de recherche (voir catalog.prerendu) : texte public seulement, une page une
adresse (canonical / hreflang), vrai 404 pour un contenu inconnu."""
import re

from django.conf import settings
from django.test import TestCase

from aide.models import ArticleAide, CategorieAide

from .models import Country, Cours, Lesson, LessonType, StatutContenu, Subject

SECRET = "SOLUTION-RESERVEE-AUX-ABONNES"


def _alternates(html):
    return dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)">', html))


def _canonical(html):
    return re.search(r'<link rel="canonical" href="([^"]+)">', html).group(1)


class PrerenduTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        pays, _ = Country.objects.get_or_create(
            code="CM", defaults={"label": "Cameroun", "dial_code": "+237", "currency": "XAF"},
        )
        cls.base = settings.FRONTEND_URL
        cls.fr = Subject.objects.create(country=pays, code="PRE_MATHS", label="Mathématiques", langue="fr")
        cls.en = Subject.objects.create(country=pays, code="PRE_GCE_MATHS", label="Mathematics", langue="en")
        sections = [
            {"type": "accroche", "contenu_markdown": "Texte d'accroche public avec $x_1 + y_2$."},
            {"type": "exercices_application", "contenu_markdown": SECRET, "exercices": [{"enonce_markdown": SECRET}]},
        ]
        cls.cours_fr = Cours.objects.create(
            external_id="pre-cours-fr", titre="Dériver une fonction", subject=cls.fr, sous_theme="Dérivation",
            sections_raw=sections, content_markdown=f"Texte d'accroche\n\n{SECRET}", statut=StatutContenu.VALIDE,
        )
        cls.cours_en = Cours.objects.create(
            external_id="pre-cours-en", titre="Algebra basics", subject=cls.en,
            sections_raw=sections, content_markdown=f"Intro\n\n{SECRET}", statut=StatutContenu.VALIDE,
        )
        cls.brouillon = Cours.objects.create(
            external_id="pre-cours-brouillon", titre="Pas publié", subject=cls.fr, statut=StatutContenu.BROUILLON,
        )
        cls.epreuve = Lesson.objects.create(
            title="Maths BAC C 2023", subject=cls.fr, lesson_type=LessonType.CORR, year=2023,
            content_markdown="Énoncé public de l'épreuve.", statut=StatutContenu.VALIDE,
        )
        cls.aide = ArticleAide.objects.create(
            slug="comment-payer", categorie=CategorieAide.choices[0][0], titre_fr="Comment payer ?",
            resume_fr="Les moyens de paiement.", corps_fr="## Payer\n\nPar mobile money.",
        )

    def get(self, chemin):
        return self.client.get(f"/prerendu/{chemin}")

    def test_cours_francais_texte_libre_et_canonical_sur_le_lecteur(self):
        reponse = self.get(f"cours/{self.cours_fr.slug}")
        self.assertEqual(reponse.status_code, 200)
        html = reponse.content.decode()
        self.assertIn("<h1>Dériver une fonction</h1>", html)
        self.assertIn("<title>Dériver une fonction | ", html)
        self.assertIn("Texte d'accroche public", html)
        # La formule LaTeX reste intacte (jamais lue comme de l'italique Markdown).
        self.assertIn("$x_1 + y_2$", html)
        # La fiche redirige vers le lecteur : c'est lui, la page canonique.
        self.assertEqual(_canonical(html), f"{self.base}/cours/{self.cours_fr.slug}/lire")
        self.assertEqual(_alternates(html), {})
        self.assertIn('<html lang="fr">', html)

    def test_cours_jamais_les_exercices_d_application_payants(self):
        for chemin in (f"cours/{self.cours_fr.slug}", f"cours/{self.cours_fr.slug}/lire", f"en/lessons/{self.cours_fr.slug}/read"):
            self.assertNotIn(SECRET, self.get(chemin).content.decode(), chemin)

    def test_reponse_propre_au_user_agent_jamais_mise_en_cache_partagee(self):
        reponse = self.get(f"cours/{self.cours_fr.slug}/lire")
        self.assertIn("private", reponse["Cache-Control"])
        self.assertIn("User-Agent", reponse["Vary"])

    def test_cours_francais_sous_en_a_pour_canonical_la_page_francaise(self):
        html = self.get(f"en/lessons/{self.cours_fr.slug}/read").content.decode()
        self.assertEqual(_canonical(html), f"{self.base}/cours/{self.cours_fr.slug}/lire")
        self.assertEqual(_alternates(html), {})

    def test_cours_en_anglais_une_adresse_par_langue_avec_hreflang(self):
        slug = self.cours_en.slug
        fr, en = f"{self.base}/cours/{slug}/lire", f"{self.base}/en/lessons/{slug}/read"
        page_fr = self.get(f"cours/{slug}/lire").content.decode()
        page_en = self.get(f"en/lessons/{slug}/read").content.decode()
        self.assertEqual(_canonical(page_fr), fr)
        self.assertEqual(_canonical(page_en), en)
        for html in (page_fr, page_en):
            self.assertEqual(_alternates(html), {"fr": fr, "en": en, "x-default": fr})
            self.assertIn('<html lang="en">', html)

    def test_epreuve_sujet_public_canonical_sur_la_fiche_pas_sur_le_lecteur(self):
        attendu = f"{self.base}/cm/epreuves/{self.epreuve.slug}"
        for chemin in (f"cm/epreuves/{self.epreuve.slug}", f"cm/epreuves/{self.epreuve.slug}/lire", f"epreuves/{self.epreuve.slug}"):
            html = self.get(chemin).content.decode()
            self.assertEqual(_canonical(html), attendu, chemin)
            self.assertIn("Énoncé public de l'épreuve.", html)
            self.assertIn("<h1>Maths BAC C 2023</h1>", html)

    def test_article_d_aide_non_traduit_une_seule_adresse(self):
        html = self.get("aide/comment-payer").content.decode()
        self.assertIn("Par mobile money.", html)
        self.assertEqual(_canonical(html), f"{self.base}/aide/comment-payer")
        sous_en = self.get("en/help/comment-payer").content.decode()
        self.assertEqual(_canonical(sous_en), f"{self.base}/aide/comment-payer")
        self.assertEqual(_alternates(sous_en), {})

    def test_contenu_inconnu_ou_brouillon_repond_404_et_noindex(self):
        for chemin in ("cours/n-existe-pas/lire", f"cours/{self.brouillon.slug}", "cm/epreuves/n-existe-pas", "aide/inconnu"):
            reponse = self.get(chemin)
            self.assertEqual(reponse.status_code, 404, chemin)
            self.assertIn('<meta name="robots" content="noindex">', reponse.content.decode())
