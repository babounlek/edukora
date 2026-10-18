"""URLs publiques en anglais : `/en/cm/past-papers/x/read` au lieu de `/en/cm/epreuves/x/lire`.

La table des segments existe en TROIS endroits qui doivent rester d'accord :
  - frontend/src/lib/i18n/segments-url.json  (routeur, liens, canonical/hreflang)
  - backend/catalog/segments_url.json        (sitemap, aperçus de liens, liens des PDF) : copie
  - docker/caddy/Caddyfile                   (aperçus de liens, redirections 301) : généré
Ces tests échouent dès qu'ils divergent. Ceux qui lisent le dépôt hors du dossier backend sont ignorés
quand ce dossier n'existe pas (exécution dans le conteneur).
"""
import importlib.util
import json
import re
from pathlib import Path

from django.test import SimpleTestCase

from catalog import segments_url
from catalog.segments_url import chemin_anglais, chemin_interne, chemin_public

RACINE = Path(__file__).resolve().parents[2]
JSON_FRONTEND = RACINE / "frontend" / "src" / "lib" / "i18n" / "segments-url.json"
CADDYFILE = RACINE / "docker" / "caddy" / "Caddyfile"
GENERATEUR = RACINE / "scripts" / "generer_caddy_segments.py"


def _exemple(patron):
    """Un chemin d'exemple : le pays est un vrai code (deux lettres), les autres segments dynamiques une valeur neutre."""
    return re.sub(r":(\w+)", lambda m: "cm" if m.group(1) == "country" else f"valeur-{m.group(1)}", patron)


class TraductionTests(SimpleTestCase):
    def test_traduit_dans_les_deux_sens(self):
        self.assertEqual(
            chemin_public("/cm/epreuves/physics-gce-ordinary-level-2023-paper-1/lire", "en"),
            "/en/cm/past-papers/physics-gce-ordinary-level-2023-paper-1/read",
        )
        self.assertEqual(chemin_public("/cm/epreuves/x/lire", "fr"), "/cm/epreuves/x/lire")
        self.assertEqual(chemin_public("/cm", "en"), "/en/cm")
        self.assertEqual(chemin_public("/cours/algebra", "en"), "/en/lessons/algebra")
        self.assertEqual(chemin_interne("/cm/past-papers/x/read"), "/cm/epreuves/x/lire")

    def test_ne_traduit_jamais_un_segment_dynamique(self):
        self.assertEqual(chemin_anglais("/cm/epreuves/cours"), "/cm/past-papers/cours")
        self.assertEqual(chemin_anglais("/cours/epreuves"), "/lessons/epreuves")

    def test_chemin_inconnu_rendu_tel_quel(self):
        self.assertEqual(chemin_anglais("/n-importe/quoi/du-tout"), "/n-importe/quoi/du-tout")
        # une ancienne forme française sous /en n'est pas une route anglaise
        self.assertEqual(chemin_interne("/cm/epreuves/x"), "/cm/epreuves/x")

    def test_chaque_patron_fait_l_aller_retour(self):
        for patron in segments_url.PATRONS_INTERNES:
            interne = _exemple(patron)
            anglais = chemin_anglais(interne)
            self.assertEqual(chemin_interne(anglais), interne, patron)
            for francais in segments_url.SEGMENTS_EN:
                if francais in patron.split("/"):
                    self.assertNotIn(francais, anglais.split("/"), f"{patron} -> {anglais}")


class CoherenceDesCopiesTests(SimpleTestCase):
    def test_la_table_backend_est_la_copie_exacte_de_celle_du_frontend(self):
        if not JSON_FRONTEND.is_file():
            self.skipTest("dossier frontend absent (exécution dans le conteneur)")
        frontend = json.loads(JSON_FRONTEND.read_text(encoding="utf-8"))
        self.assertEqual(frontend["segments"], segments_url.SEGMENTS_EN)
        self.assertEqual(frontend["patrons"], segments_url.PATRONS_INTERNES)

    def test_le_caddyfile_est_a_jour_avec_la_table(self):
        if not (CADDYFILE.is_file() and GENERATEUR.is_file()):
            self.skipTest("Caddyfile ou générateur absent (exécution dans le conteneur)")
        spec = importlib.util.spec_from_file_location("generer_caddy_segments", GENERATEUR)
        generateur = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generateur)
        with open(CADDYFILE, encoding="utf-8", newline="") as f:
            contenu = f.read()
        donnees = json.loads(JSON_FRONTEND.read_text(encoding="utf-8"))
        self.assertEqual(
            generateur.appliquer(contenu, generateur.generer(donnees)), contenu,
            "Caddyfile obsolète : python scripts/generer_caddy_segments.py --ecrire",
        )

    def test_la_regle_d_apercu_de_caddy_couvre_les_pages_de_detail_dans_les_deux_langues(self):
        if not CADDYFILE.is_file():
            self.skipTest("Caddyfile absent (exécution dans le conteneur)")
        regles = re.findall(r"path_regexp (\^/\(en/\)\?.*\$)", CADDYFILE.read_text(encoding="utf-8"))
        self.assertEqual(len(regles), 1, "règle d'aperçu introuvable dans le Caddyfile")
        regle = re.compile(regles[0])
        details = [p for p in segments_url.PATRONS_INTERNES
                   if re.search(r"/(epreuves|cours|epreuves-inedites)/:\w+(/lire)?$", p)]
        self.assertGreaterEqual(len(details), 5)
        for patron in details:
            interne = _exemple(patron)
            self.assertTrue(regle.match(interne), f"FR non couvert : {interne}")
            self.assertTrue(regle.match(chemin_public(interne, "en")), f"EN non couvert : {chemin_public(interne, 'en')}")

    def test_les_redirections_301_couvrent_toutes_les_routes_traduites(self):
        if not CADDYFILE.is_file():
            self.skipTest("Caddyfile absent (exécution dans le conteneur)")
        contenu = CADDYFILE.read_text(encoding="utf-8")
        a_traduire = [p for p in segments_url.PATRONS_INTERNES
                      if any(s in segments_url.SEGMENTS_EN for s in p.split("/"))]
        self.assertEqual(contenu.count("redir @seg_en_"), len(a_traduire))
        self.assertEqual(contenu.count("{qs_en} 301"), len(a_traduire))


class LiensDesPdfTests(SimpleTestCase):
    """Les liens imprimés dans les PDF mènent à la page de la langue du contenu."""

    def _lecon(self, langue):
        from types import SimpleNamespace

        return SimpleNamespace(slug="physics-2023", subject=SimpleNamespace(langue=langue))

    def test_sujet_d_epreuve(self):
        from django.test import override_settings

        from catalog.sujet_pdf import _lesson_deep_link

        header = {"pays": {"code": "CM"}}
        with override_settings(PDF_SITE_URL="https://edukora.africa"):
            self.assertEqual(
                _lesson_deep_link(self._lecon("en"), header),
                "https://edukora.africa/en/cm/past-papers/physics-2023?ref=pdf_sujet",
            )
            self.assertEqual(
                _lesson_deep_link(self._lecon("fr"), header),
                "https://edukora.africa/cm/epreuves/physics-2023?ref=pdf_sujet",
            )

    def test_epreuve_inedite(self):
        from types import SimpleNamespace

        from django.test import override_settings

        from inedit.sujet_pdf import _epreuve_deep_link

        def epreuve(langue):
            cursus = SimpleNamespace(first=lambda: SimpleNamespace(country=SimpleNamespace(code="CM")))
            return SimpleNamespace(slug="mock-1", cursus=cursus, subject=SimpleNamespace(langue=langue))

        with override_settings(PDF_SITE_URL="https://edukora.africa"):
            self.assertEqual(
                _epreuve_deep_link(epreuve("en")), "https://edukora.africa/en/cm/mock-papers/mock-1?ref=pdf_sujet_inedit",
            )
            self.assertEqual(
                _epreuve_deep_link(epreuve("fr")), "https://edukora.africa/cm/epreuves-inedites/mock-1?ref=pdf_sujet_inedit",
            )

    def test_lien_vers_le_cours_dans_un_quiz(self):
        from django.test import override_settings

        from quiz.pdf import _resolve_cours_links

        with override_settings(PDF_SITE_URL="https://edukora.africa"):
            self.assertEqual(
                _resolve_cours_links("[COURS_LINK:algebra]", "See the lesson", "en"),
                "[See the lesson](https://edukora.africa/en/lessons/algebra)",
            )
            self.assertEqual(
                _resolve_cours_links("[COURS_LINK:algebra]", "Voir le cours"),
                "[Voir le cours](https://edukora.africa/cours/algebra)",
            )
