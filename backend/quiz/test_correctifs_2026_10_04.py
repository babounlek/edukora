import json
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase, override_settings

from catalog.models import Country, Tag
from quiz.ingestion import ingest_competence_item
from quiz.models import CompetenceItem
from quiz.tests import _item_payload

CORRIGE_A = "### Rappel de méthode\n\nx\n\n### Corrigé\n\navant A"


class AppliquerCorrectifsQuizTests(TestCase):
    """Rejeu des correctifs de contenu du Mode Quiz sur une autre base : retrouvés par
    external_id, appliqués une seule fois, jamais par-dessus une modification manuelle."""

    def setUp(self):
        self.country = Country.objects.get(code="CM")
        Tag.objects.create(name="dérivation")
        self.a, _ = ingest_competence_item(_item_payload(external_id="cqc-a", corrige_markdown=CORRIGE_A), self.country)
        self.b, _ = ingest_competence_item(
            _item_payload(external_id="cqc-b", enonce_markdown="Dans le montage précédent, calculer $x$.",
                          corrige_markdown="### Rappel de méthode\n\nr\n\n### Corrigé\n\n$x=2$."),
            self.country,
        )
        self.c, _ = ingest_competence_item(
            _item_payload(external_id="cqc-c", corrige_markdown="### Rappel de méthode\n\nx\n\n### Corrigé\n\nRETOUCHÉ À LA MAIN"),
            self.country,
        )
        self.d, _ = ingest_competence_item(
            _item_payload(external_id="cqc-d", enonce_markdown="Texte avec ANCIENNE_PHRASE dedans."), self.country,
        )
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        tmp = Path(self.tmp.name)
        self.images = tmp / "images"
        self.images.mkdir()
        from PIL import Image

        Image.new("RGB", (30, 20), "white").save(self.images / "cqc-a_fig_1.webp", format="WEBP")
        self.media = tmp / "media"
        self.media.mkdir()
        figure = lambda ext_id, avant: {  # noqa: E731
            "external_id": ext_id,
            "corrige_avant": avant,
            "corrige_modele": "### Rappel de méthode\n\nx\n\n### Corrigé\n\n![fig-1](%s_fig_1.png)\n\navant A" % ext_id,
            "figures": [{
                "id": "fig-1", "fichier": f"{ext_id}_fig_1.png", "image": f"figures/cm/quiz/{ext_id}_fig_1.webp",
                "type": "courbe", "legende": "Courbe de f", "origine": "corrige",
            }],
        }
        bundle = {
            "version": 1, "date": "2026-10-04",
            "figures": [
                figure("cqc-a", CORRIGE_A),
                figure("cqc-c", CORRIGE_A),          # l'item en base a été retouché : ignoré
                figure("cqc-absent", CORRIGE_A),     # pas dans cette base : ignoré
            ],
            "reecritures": [{
                "external_id": "cqc-b",
                "enonce_avant": "Dans le montage précédent, calculer $x$.",
                "enonce_apres": "Un montage est décrit en entier ici, calculer $x$.",
                "corrige_avant": "### Rappel de méthode\n\nr\n\n### Corrigé\n\n$x=2$.",
                "corrige_apres": "### Rappel de méthode\n\nr\n\n### Corrigé\n\n$x=2$.",
            }],
            "remplacements": [{
                "description": "test", "old": "ANCIENNE_PHRASE", "new": "NOUVELLE_PHRASE",
                "champs": ["quiz.CompetenceItem.enonce_markdown"],
            }],
        }
        self.bundle = tmp / "bundle.json"
        self.bundle.write_text(json.dumps(bundle), encoding="utf-8")

    def _run(self, *extra):
        out = StringIO()
        with override_settings(MEDIA_ROOT=str(self.media)):
            call_command("appliquer_correctifs_quiz_2026_10_04", "--bundle", str(self.bundle),
                         "--images-dir", str(self.images), *extra, stdout=out)
        return out.getvalue()

    def test_simulation_ne_modifie_rien(self):
        out = self._run()
        self.assertIn("simulation", out)
        self.assertIn("'appliquées': 1", out)
        self.a.refresh_from_db()
        self.assertEqual(self.a.corrige_markdown, CORRIGE_A)
        self.assertFalse(self.a.figures.exists())
        self.b.refresh_from_db()
        self.assertIn("précédent", self.b.enonce_markdown)

    def test_apply_ajoute_la_figure_reecrit_et_remplace(self):
        out = self._run("--apply")
        self.assertIn("modifié depuis", out)
        self.a.refresh_from_db()
        figure = self.a.figures.get()
        self.assertEqual(figure.external_id, "fig-1")
        self.assertEqual(figure.origine, "CORRIGE")
        self.assertIn("![Courbe de f](/media/figures/cm/quiz/cqc-a_fig_1.webp)", self.a.corrige_markdown)
        self.assertNotIn("![fig-1]", self.a.corrige_markdown)
        self.assertTrue((self.media / "figures" / "cm" / "quiz" / "cqc-a_fig_1.webp").is_file())
        self.b.refresh_from_db()
        self.assertEqual(self.b.enonce_markdown, "Un montage est décrit en entier ici, calculer $x$.")
        self.d.refresh_from_db()
        self.assertEqual(self.d.enonce_markdown, "Texte avec NOUVELLE_PHRASE dedans.")

    def test_item_retouche_a_la_main_est_laisse_intact(self):
        self._run("--apply")
        self.c.refresh_from_db()
        self.assertIn("RETOUCHÉ À LA MAIN", self.c.corrige_markdown)
        self.assertFalse(self.c.figures.exists())

    def test_idempotent(self):
        self._run("--apply")
        before = (CompetenceItem.objects.get(external_id="cqc-a").corrige_markdown,
                  CompetenceItem.objects.get(external_id="cqc-b").enonce_markdown)
        out = self._run("--apply")
        self.assertIn("'déjà faites': 1", out)
        self.assertEqual(CompetenceItem.objects.get(external_id="cqc-a").figures.count(), 1)
        after = (CompetenceItem.objects.get(external_id="cqc-a").corrige_markdown,
                 CompetenceItem.objects.get(external_id="cqc-b").enonce_markdown)
        self.assertEqual(before, after)

    def test_tolere_l_ordre_inverse_avec_la_reparation_latex(self):
        # Base d'origine : un \ne coupé en saut de ligne + "e" dans le corrigé « avant » du
        # paquet ; après réparation côté base, la comparaison doit tout de même reconnaître l'item.
        avant_casse = "### Rappel de méthode\n\nx\n\n### Corrigé\n\nsi $x" + chr(10) + "e0$"
        avant_repare = "### Rappel de méthode\n\nx\n\n### Corrigé\n\nsi $x" + chr(92) + "ne0$"
        CompetenceItem.objects.filter(external_id="cqc-a").update(corrige_markdown=avant_repare)
        data = json.loads(self.bundle.read_text(encoding="utf-8"))
        data["figures"][0]["corrige_avant"] = avant_casse
        data["figures"][0]["corrige_modele"] = data["figures"][0]["corrige_modele"].replace("avant A", "si $x" + chr(10) + "e0$")
        self.bundle.write_text(json.dumps(data), encoding="utf-8")
        self._run("--apply")
        a = CompetenceItem.objects.get(external_id="cqc-a")
        self.assertTrue(a.figures.exists())
        self.assertIn("si $x" + chr(92) + "ne0$", a.corrige_markdown)
