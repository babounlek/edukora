from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from catalog.ingestion import sciences_si_serie_a
from catalog.models import (
    Country, Cursus, Examen, Lesson, LessonType, Origine, Series, StatutContenu, Subject, Tag,
)
from quiz.models import CompetenceItem
from quiz.tests import _make_competence_item


class _Base(TestCase):
    def setUp(self):
        self.pays = Country.objects.get_or_create(code="CM", defaults={"label": "Cameroun", "dial_code": "+237", "currency": "XAF"})[0]
        self.serie_a = Series.objects.get_or_create(country=self.pays, code="A", defaults={"label": "Littéraire"})[0]
        self.serie_c = Series.objects.get_or_create(country=self.pays, code="C", defaults={"label": "Maths"})[0]
        self.bac_a = Cursus.objects.get_or_create(country=self.pays, examen=Examen.BAC, series=self.serie_a)[0]
        self.bac_c = Cursus.objects.get_or_create(country=self.pays, examen=Examen.BAC, series=self.serie_c)[0]
        self.svt = Subject.objects.get_or_create(country=self.pays, code="SVT", defaults={"label": "Sciences de la Vie et de la Terre"})[0]

    def _sujet(self, cursus, titre):
        lesson = Lesson.objects.create(
            title=titre, subject=self.svt, year=2024, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE, origine=Origine.OFFICIEL,
        )
        lesson.cursus.add(*cursus)
        return lesson


class RegleIngestionTests(_Base):
    def test_contenu_de_serie_a_seule_va_en_sciences_s_il_y_a_une_matiere_sciences(self):
        sciences = Subject.objects.create(country=self.pays, code="SCIENCES", label="Sciences")
        self.assertEqual(sciences_si_serie_a(self.svt, [self.bac_a]), sciences)

    def test_contenu_partage_avec_une_autre_serie_reste_en_svt(self):
        Subject.objects.create(country=self.pays, code="SCIENCES", label="Sciences")
        self.assertEqual(sciences_si_serie_a(self.svt, [self.bac_a, self.bac_c]), self.svt)
        self.assertEqual(sciences_si_serie_a(self.svt, [self.bac_c]), self.svt)

    def test_sans_matiere_sciences_rien_ne_change(self):
        self.assertEqual(sciences_si_serie_a(self.svt, [self.bac_a]), self.svt)


class SeparationSerieATests(_Base):
    def _lancer(self, *args):
        sortie = StringIO()
        call_command("separer_sciences_serie_a", *args, stdout=sortie)
        return sortie.getvalue()

    def test_simulation_n_ecrit_rien(self):
        self._sujet([self.bac_a], "SVT A")
        self._lancer()
        self.assertFalse(Subject.objects.filter(code="SCIENCES").exists())
        self.assertEqual(Lesson.objects.filter(subject=self.svt).count(), 1)

    def test_deplace_le_propre_a_la_serie_a_et_duplique_les_items_partages(self):
        propre = self._sujet([self.bac_a], "SVT A")
        autre = self._sujet([self.bac_c], "SVT C")
        theme = Tag.objects.create(name="meiose-test")
        item_a = _make_competence_item(self.svt, [self.bac_a], theme=theme, numero="a", external_id="cqc-a")
        item_partage = _make_competence_item(self.svt, [self.bac_a, self.bac_c], theme=theme, numero="p", external_id="cqc-p")

        self._lancer("--appliquer")
        sciences = Subject.objects.get(country=self.pays, code="SCIENCES")
        self.assertEqual(sciences.equivalent_code, "SVT")

        propre.refresh_from_db(); autre.refresh_from_db()
        self.assertEqual(propre.subject, sciences)
        self.assertEqual(autre.subject, self.svt)

        item_a.refresh_from_db(); item_partage.refresh_from_db()
        self.assertEqual(item_a.subject, sciences)                       # propre à A : déplacé
        self.assertEqual(item_partage.subject, self.svt)                 # original : reste en SVT...
        self.assertEqual(set(item_partage.cursus.all()), {self.bac_c})   # ...sans la série A
        copie = CompetenceItem.objects.get(external_id="cqc-p-sciences-a")
        self.assertEqual(copie.subject, sciences)
        self.assertEqual(set(copie.cursus.all()), {self.bac_a})          # copie réservée à A
        self.assertEqual(copie.enonce_markdown, item_partage.enonce_markdown)

    def test_idempotent(self):
        self._sujet([self.bac_a], "SVT A")
        _make_competence_item(self.svt, [self.bac_a, self.bac_c], numero="p", external_id="cqc-p")
        self._lancer("--appliquer")
        total = CompetenceItem.objects.count()
        sortie = self._lancer("--appliquer")
        self.assertEqual(CompetenceItem.objects.count(), total)
        self.assertIn("propres à la série A : 0", sortie)


class RenommageTitresEtSlugsTests(_Base):
    def setUp(self):
        super().setUp()
        import tempfile
        from pathlib import Path
        from unittest import mock
        from catalog import slugs_renommes
        from catalog.management.commands import renommer_sciences_serie_a as cmd

        self.table = Path(tempfile.mkdtemp()) / "slugs_renommes.json"
        self.table.write_text("{}", encoding="utf-8")
        for module in (slugs_renommes, cmd):
            patcher = mock.patch.object(module, "FICHIER", self.table)
            patcher.start()
            self.addCleanup(patcher.stop)
        slugs_renommes.recharger()
        self.addCleanup(slugs_renommes.recharger)
        self.sciences = Subject.objects.create(country=self.pays, code="SCIENCES", label="Sciences")

    def _sujet_sciences(self, titre):
        lesson = self._sujet([self.bac_a], titre)
        Lesson.objects.filter(pk=lesson.pk).update(subject=self.sciences)
        lesson.refresh_from_db()
        return lesson

    def _lancer(self, *args):
        call_command("renommer_sciences_serie_a", *args, stdout=StringIO())

    def test_simulation_ne_change_rien(self):
        lesson = self._sujet_sciences("Sciences de la Vie et de la Terre BAC A 2024")
        ancien = lesson.slug
        self._lancer()
        lesson.refresh_from_db()
        self.assertEqual((lesson.title, lesson.slug), ("Sciences de la Vie et de la Terre BAC A 2024", ancien))

    def test_titre_et_slug_corriges_et_ancienne_adresse_toujours_valable(self):
        lesson = self._sujet_sciences("Sciences de la Vie et de la Terre BAC A 2024")
        ancien = lesson.slug
        autre_matiere = self._sujet([self.bac_c], "Sciences de la Vie et de la Terre BAC C 2024")  # reste en SVT
        self._lancer("--appliquer")
        lesson.refresh_from_db(); autre_matiere.refresh_from_db()
        self.assertEqual(lesson.title, "Sciences BAC A 2024")
        self.assertEqual(lesson.slug, "sciences-bac-a-2024")
        self.assertEqual(autre_matiere.title, "Sciences de la Vie et de la Terre BAC C 2024")
        self.assertEqual(list(Lesson.objects.par_slug_ou_id(ancien)), [lesson])
        self.assertEqual(list(Lesson.objects.par_slug_ou_id("sciences-bac-a-2024")), [lesson])

    def test_idempotent(self):
        self._sujet_sciences("Sciences de la Vie et de la Terre BAC A 2024")
        self._lancer("--appliquer")
        avant = self.table.read_text(encoding="utf-8")
        self._lancer("--appliquer")
        self.assertEqual(self.table.read_text(encoding="utf-8"), avant)
