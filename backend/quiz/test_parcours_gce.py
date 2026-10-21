"""
Parcours par thème du GCE : les variantes d'une même notion sont regroupées (TAGS_ALIAS_PAR_MATIERE).

Les lots GCE ont nommé la même notion de trois façons en Physique (« temperature scales », « temperature measurement »,
« thermometers and temperature scales ») et deux en moments (« moments of forces », « turning effect of forces »,
« moments and equilibrium ») : chacune n'apparaissait que dans une épreuve, donc sous le plancher d'occurrences du
classement et absente de « Ma progression », alors que leurs cours et leurs quiz existent. Regroupées, elles passent le
plancher. Seules les variantes d'une MÊME notion sont regroupées - jamais un thème et son sous-thème (« pulleys » reste à
part de « simple machines »), règle de granularité du classement.
"""
from django.test import TestCase

from catalog.models import Cursus, Examen, Subject, Tag
from users.models import User

from .services import (
    PARCOURS_FREQUENCE_OCCURRENCES_MIN, SEUIL_MINIMUM_THEMES_PARCOURS, TAGS_ALIAS_PAR_MATIERE,
    construire_parcours_par_frequence,
)
from .tests import _make_lesson_avec_themes


class ParcoursGcePhysiqueTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677200901", password="x")
        self.profil = self.user.profils.first()
        self.subject = Subject.objects.get(country__code="CM", code="GCE_PHYSICS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.GCE_OL, series__isnull=True)
        # De quoi dépasser le seuil de fiabilité du classement : des thèmes de remplissage dans chaque épreuve.
        self.remplissage = [Tag.objects.create(name=f"filler-{i}") for i in range(SEUIL_MINIMUM_THEMES_PARCOURS)]

    def _epreuves(self, variantes):
        """
        SEUIL_MINIMUM_THEMES_PARCOURS épreuves officielles (le classement normal en exige autant ; la Physique GCE en a
        exactement 8) : les premières portent chacune UNE variante (plus le remplissage), les autres le remplissage seul.
        """
        tags = {nom: Tag.objects.get_or_create(name=nom)[0] for nom in variantes}
        for i in range(SEUIL_MINIMUM_THEMES_PARCOURS):
            themes = [*self.remplissage] + ([tags[variantes[i]]] if i < len(variantes) else [])
            _make_lesson_avec_themes(self.subject, self.cursus, f"Physics {i}", [themes])

    def _noms(self):
        themes = construire_parcours_par_frequence(self.profil, self.cursus, self.subject)
        return {t["intitule"]: t for t in themes or []}

    def test_les_trois_ecritures_de_la_temperature_ne_forment_qu_un_theme(self):
        self._epreuves(["temperature scales", "temperature measurement", "thermometers and temperature scales"])

        noms = self._noms()

        self.assertEqual(noms["thermometers and temperature scales"]["nb_epreuves"], 3)
        self.assertNotIn("temperature scales", noms)
        self.assertNotIn("temperature measurement", noms)

    def test_les_ecritures_des_moments_ne_forment_qu_un_theme(self):
        self._epreuves(["moments of forces", "turning effect of forces", "moments and equilibrium"])

        noms = self._noms()

        self.assertEqual(noms["moments and equilibrium"]["nb_epreuves"], 3)
        self.assertNotIn("moments of forces", noms)
        self.assertNotIn("turning effect of forces", noms)

    def test_un_theme_vu_dans_une_seule_epreuve_reste_sous_le_plancher(self):
        self._epreuves(["pulleys", "simple machines", "simple machines"])

        noms = self._noms()

        self.assertEqual(noms["simple machines"]["nb_epreuves"], 2)
        self.assertGreaterEqual(2, PARCOURS_FREQUENCE_OCCURRENCES_MIN)
        self.assertNotIn("pulleys", noms)  # un seul passage : pas un thème qui « revient »

    def test_un_sous_theme_n_est_jamais_absorbe_par_son_parent(self):
        alias = TAGS_ALIAS_PAR_MATIERE["GCE_PHYSICS"]
        for sous_theme in ("pulleys", "pressure in fluids", "speed of sound", "wave phenomena", "graph plotting"):
            self.assertNotIn(sous_theme, alias)

    # Le titre de la vue « par thème » suit la langue du cursus : un élève du GCE ne le lit plus en français.
    def test_le_titre_est_en_anglais_pour_le_gce(self):
        from .services import construire_parcours

        self._epreuves(["temperature scales", "moments of forces"])

        modules = construire_parcours(self.profil, self.cursus, self.subject)

        self.assertEqual(modules[0]["titre"], "The topics that come up most in the exam")

    def test_le_titre_reste_en_francais_pour_un_examen_francophone(self):
        from .textes import texte

        self.assertEqual(texte("parcours.titre_themes", "fr"), "Les thèmes qui reviennent le plus à l'examen")
        self.assertEqual(texte("parcours.titre_themes", "xx"), "Les thèmes qui reviennent le plus à l'examen")
