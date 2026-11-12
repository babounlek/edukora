"""Pages d'atterrissage par examen (voir catalog.pages_examen) : URL, données, API, prérendu des moteurs, aperçu de
partage, sitemap. Rien de payant n'y paraît : des chiffres, des titres, l'indication « corrigé libre »."""
import re

from django.conf import settings
from django.test import TestCase

from . import pages_examen
from .apercu_partage import infos_page
from .models import Country, Cursus, Examen, Lesson, LessonType, StatutContenu, Subject
from .segments_url import chemin_public

SECRET = "CORRIGE-RESERVE-AUX-ABONNES"


class PagesExamenTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        pays, _ = Country.objects.get_or_create(
            code="CM", defaults={"label": "Cameroun", "dial_code": "+237", "currency": "XAF"},
        )
        cls.bepc, _ = Cursus.objects.get_or_create(country=pays, examen=Examen.BEPC, series=None)
        cls.gce, _ = Cursus.objects.get_or_create(country=pays, examen=Examen.GCE_OL, series=None)
        cls.vide, _ = Cursus.objects.get_or_create(country=pays, examen=Examen.GCE_AL, series=None)
        maths = Subject.objects.create(country=pays, code="PEX_MATHS", label="Mathématiques", langue="fr")
        physique = Subject.objects.create(country=pays, code="PEX_PHYS", label="Physique", langue="fr")
        anglais = Subject.objects.create(country=pays, code="PEX_GCE", label="Mathematics", langue="en")

        def epreuve(titre, sujet, annee, cursus, **extra):
            lesson = Lesson.objects.create(
                title=titre, subject=sujet, lesson_type=LessonType.CORR, year=annee,
                content_markdown=f"Énoncé. {SECRET}", statut=StatutContenu.VALIDE, **extra,
            )
            lesson.cursus.add(cursus)
            return lesson

        cls.libre = epreuve("Maths BEPC 2026", maths, 2026, cls.bepc, est_vitrine=True)
        cls.payante = epreuve("Maths BEPC 2024", maths, 2024, cls.bepc)
        epreuve("Physique BEPC 2020", physique, 2020, cls.bepc)
        epreuve("Mathematics GCE O Level 2019", anglais, 2019, cls.gce)
        brouillon = Lesson.objects.create(
            title="Brouillon BEPC", subject=maths, lesson_type=LessonType.CORR, year=2025,
            statut=StatutContenu.BROUILLON,
        )
        brouillon.cursus.add(cls.bepc)

    # --- slug et données

    def test_slug_d_un_cursus(self):
        self.assertEqual(pages_examen.slug_cursus(self.bepc), "bepc")
        self.assertTrue(pages_examen.slug_cursus(self.gce).startswith("gce"))

    def test_seuls_les_examens_avec_epreuves_publiees_ont_une_page(self):
        slugs = [pages_examen.slug_cursus(c) for c, _ in pages_examen.cursus_avec_epreuves("cm")]
        self.assertIn("bepc", slugs)
        self.assertIn(pages_examen.slug_cursus(self.gce), slugs)
        # GCE A Level n'a aucune épreuve : pas de page vide à indexer.
        self.assertNotIn(pages_examen.slug_cursus(self.vide), slugs)

    def test_donnees_comptent_les_epreuves_publiees_et_les_corriges_libres(self):
        donnees = pages_examen.donnees_examen("cm", "bepc")
        self.assertEqual(donnees["nb_epreuves"], 3)  # le brouillon n'est pas compté
        self.assertEqual(donnees["nb_epreuves_libres"], 1)
        self.assertEqual((donnees["annee_min"], donnees["annee_max"]), (2020, 2026))
        self.assertEqual(donnees["nb_matieres"], 2)
        self.assertEqual(donnees["epreuves"][0]["title"], "Maths BEPC 2026")  # la plus récente d'abord
        self.assertTrue(donnees["epreuves"][0]["libre"])
        self.assertNotIn("Brouillon BEPC", [e["title"] for e in donnees["epreuves"]])

    def test_examen_inconnu_ou_sans_epreuve_n_existe_pas(self):
        self.assertIsNone(pages_examen.donnees_examen("cm", "inconnu"))
        self.assertIsNone(pages_examen.donnees_examen("cm", pages_examen.slug_cursus(self.vide)))
        self.assertIsNone(pages_examen.donnees_examen("zz", "bepc"))

    def test_textes_ne_promettent_que_ce_qui_est_compte(self):
        donnees = pages_examen.donnees_examen("cm", "bepc")
        textes = pages_examen.textes_page(donnees, "fr")
        self.assertEqual(textes["titre"], "Annales BEPC corrigées au Cameroun")
        self.assertIn("3 annales BEPC au Cameroun (2020 à 2026)", textes["description"])
        self.assertIn("1 en accès libre", textes["description"])
        # Aucun cours rattaché : la phrase n'en parle pas (et n'écrit jamais « 0 cours »).
        self.assertNotIn("0 cours", textes["intro"])

    def test_la_description_commence_par_une_majuscule_meme_avec_un_grand_total(self):
        donnees = dict(pages_examen.donnees_examen("cm", "bepc"), nb_epreuves=247)
        self.assertTrue(pages_examen.textes_page(donnees, "fr")["description"].startswith("Plus de 240 annales"))
        self.assertTrue(pages_examen.textes_page(donnees, "en")["description"].startswith("Over 240"))

    def test_grand_total_arrondi_vers_le_bas(self):
        self.assertEqual(pages_examen._arrondi(247, "fr"), "plus de 240")
        self.assertEqual(pages_examen._arrondi(247, "en"), "over 240")
        self.assertEqual(pages_examen._arrondi(7, "fr"), "7")

    # --- API

    def test_api_publique(self):
        reponse = self.client.get("/catalog/examens/cm/bepc/")
        self.assertEqual(reponse.status_code, 200)
        corps = reponse.json()
        self.assertEqual(corps["libelle"], "BEPC")
        self.assertEqual(corps["nb_epreuves"], 3)
        self.assertEqual(corps["textes"]["titre"], "Annales BEPC corrigées au Cameroun")
        # Jamais de contenu d'épreuve : seulement des titres et des chiffres.
        self.assertNotIn(SECRET, reponse.content.decode())

    def test_api_liste_des_examens_avec_page(self):
        reponse = self.client.get("/catalog/examens/cm/")
        self.assertEqual(reponse.status_code, 200)
        slugs = [e["slug"] for e in reponse.json()]
        self.assertIn("bepc", slugs)
        self.assertNotIn(pages_examen.slug_cursus(self.vide), slugs)
        self.assertIn("max-age", reponse["Cache-Control"])

    def test_le_serializer_de_cursus_donne_le_meme_slug_que_la_page(self):
        from .serializers import CursusSerializer

        self.assertEqual(CursusSerializer(self.bepc).data["slug"], pages_examen.slug_cursus(self.bepc))
        self.assertEqual(CursusSerializer(self.gce).data["slug"], pages_examen.slug_cursus(self.gce))

    def test_api_404(self):
        self.assertEqual(self.client.get("/catalog/examens/cm/inconnu/").status_code, 404)

    # --- prérendu pour les moteurs

    def get(self, chemin):
        return self.client.get(f"/prerendu/{chemin}")

    def test_prerendu_francais(self):
        reponse = self.get("cm/examens/bepc")
        self.assertEqual(reponse.status_code, 200)
        html = reponse.content.decode()
        self.assertIn("<h1>Annales BEPC corrigées au Cameroun</h1>", html)
        self.assertIn('<html lang="fr">', html)
        self.assertEqual(
            re.search(r'<link rel="canonical" href="([^"]+)">', html).group(1), f"{settings.FRONTEND_URL}/cm/examens/bepc",
        )
        # Un lien vers chaque épreuve, avec son état ; le français n'a pas de version anglaise.
        self.assertIn('href="/cm/epreuves/', html)
        self.assertIn("corrigé en accès libre", html)
        self.assertNotIn('hreflang="en"', html)

    def test_prerendu_ne_laisse_jamais_passer_un_corrige(self):
        self.assertNotIn(SECRET, self.get("cm/examens/bepc").content.decode())

    def test_prerendu_gce_en_anglais_avec_hreflang(self):
        slug = pages_examen.slug_cursus(self.gce)
        html = self.get(f"en/cm/exams/{slug}").content.decode()
        self.assertIn('<html lang="en">', html)
        self.assertIn("past papers with solutions in Cameroon", html)
        self.assertIn(f'hreflang="en" href="{settings.FRONTEND_URL}/en/cm/exams/{slug}"', html)
        self.assertIn(f'hreflang="fr" href="{settings.FRONTEND_URL}/cm/examens/{slug}"', html)

    def test_prerendu_vrai_404(self):
        for chemin in ("cm/examens/inconnu", "examens/bepc"):  # inconnu ; sans pays
            reponse = self.get(chemin)
            self.assertEqual(reponse.status_code, 404, chemin)
            self.assertIn('content="noindex"', reponse.content.decode())

    # --- aperçu de partage, URL, sitemap

    def test_apercu_de_partage(self):
        infos = infos_page("cm/examens/bepc")
        self.assertEqual(infos["titre"], "Annales BEPC corrigées au Cameroun")
        self.assertEqual(infos["chemin"], "cm/examens/bepc")
        self.assertIsNone(infos_page("cm/examens/inconnu"))
        self.assertEqual(infos_page(f"en/cm/exams/{pages_examen.slug_cursus(self.gce)}")["chemin"].split("/")[:3], ["en", "cm", "exams"])

    def test_adresse_anglaise_traduite(self):
        self.assertEqual(chemin_public("/cm/examens/gce-o-level", "en"), "/en/cm/exams/gce-o-level")

    def test_sitemap_liste_les_themes_qui_tombent_et_a_propos(self):
        xml = "".join(self.client.get(f"/sitemap-{i}.xml").content.decode() for i in (1, 2))
        for chemin in ("/cm/themes-frequents", "/en/cm/frequent-topics", "/a-propos", "/en/about"):
            self.assertIn(f"<loc>{settings.FRONTEND_URL}{chemin}</loc>", xml, chemin)

    def test_sitemap_liste_les_pages_d_examen(self):
        xml = "".join(self.client.get(f"/sitemap-{i}.xml").content.decode() for i in (1, 2))
        self.assertIn(f"<loc>{settings.FRONTEND_URL}/cm/examens/bepc</loc>", xml)
        slug = pages_examen.slug_cursus(self.gce)
        self.assertIn(f"<loc>{settings.FRONTEND_URL}/en/cm/exams/{slug}</loc>", xml)
        # Aucune page pour l'examen sans épreuve.
        self.assertNotIn(f"/examens/{pages_examen.slug_cursus(self.vide)}<", xml)
