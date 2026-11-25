"""
Le classement des thèmes d'une matière est coupé en deux (voir quiz.services) : ce qui est commun à tous les élèves
(squelette_par_frequence, gardé en cache) et ce que chaque élève a fait (progression_par_theme).

Ce qui est testé, c'est ce que cette coupe pourrait casser : la progression d'un élève servie à un autre, un résumé
qui ne dirait plus la même chose que le détail, un contenu publié qui n'apparaîtrait jamais, un appelant qui
abîmerait la copie partagée.
"""
from django.core.cache import caches
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext

from catalog.models import Cursus, Examen, Subject, Tag
from users.models import User

from .models import ModeQuiz, QuizAnswer, QuizQuestion, QuizSession
from .services import (
    SEUIL_MINIMUM_THEMES_PARCOURS, construire_parcours_par_frequence, oublier_squelettes, progression_par_theme,
    resume_parcours,
)
from .tests import _make_competence_item, _make_lesson_avec_themes, _make_question

# Un cache en mémoire propre à ces tests : celui de la configuration écrit des fichiers.
CACHE_DE_TEST = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    "parcours": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": "test-cache-parcours"},
}


class ParcoursFixture(TestCase):
    def setUp(self):
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.frequent = Tag.objects.create(name="frequent (test cache)")
        self.rare = Tag.objects.create(name="rare (test cache)")
        for i in range(SEUIL_MINIMUM_THEMES_PARCOURS):
            _make_lesson_avec_themes(
                self.subject, self.cursus, f"Lesson {i}", [[self.frequent, self.rare] if i < 2 else [self.frequent]],
            )
        self.item = _make_competence_item(self.subject, self.cursus, theme=self.frequent, numero="cache-1")
        self.aicha = self._eleve("677200101")
        self.bruno = self._eleve("677200102")

    def _eleve(self, telephone):
        return User.objects.create_user(phone_number=telephone, password="x").profils.first()

    def _repondre(self, profil, correcte=True):
        session = QuizSession.objects.create(profil=profil, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        question = QuizQuestion.objects.create(session=session, competence_item=self.item, ordre=1)
        QuizAnswer.objects.create(quiz_question=question, resultat_declare="REUSSI" if correcte else "ECHEC")

    def _theme(self, profil, nom, **options):
        themes = construire_parcours_par_frequence(profil, self.cursus, self.subject, **options)
        return next(t for t in themes if t["intitule"] == nom)


class DeuxMoitiesTests(ParcoursFixture):
    """Sans cache (le réglage des tests) : la coupe en deux ne change rien à ce qui est rendu."""

    def test_la_progression_lue_une_fois_donne_le_meme_classement(self):
        self._repondre(self.aicha)
        seul = construire_parcours_par_frequence(self.aicha, self.cursus, self.subject)
        partage = construire_parcours_par_frequence(
            self.aicha, self.cursus, self.subject, progression=progression_par_theme(self.aicha, self.cursus),
        )
        self.assertEqual(seul, partage)
        self.assertEqual(self._theme(self.aicha, self.frequent.name)["taux"], 100)

    def test_le_classement_rendu_ne_porte_pas_les_tags_internes(self):
        themes = construire_parcours_par_frequence(self.aicha, self.cursus, self.subject)
        self.assertEqual(
            set(themes[0]),
            {"id", "theme_id", "numero", "intitule", "savoir_label", "nb_epreuves", "frequence_pct", "taux",
             "nb_reponses", "maitrise", "niveau", "en_revision", "a_lu_le_cours", "has_quiz", "cours"},
        )
        self.assertEqual([t["numero"] for t in themes], ["1", "2"])

    def test_une_reponse_sans_item_de_competence_ne_casse_pas_la_lecture_globale(self):
        # Une réponse d'avant la bascule vers CompetenceItem : pas de thème à créditer.
        ancienne = _make_question(_make_lesson_avec_themes(self.subject, self.cursus, "Ancienne", []), "1")
        session = QuizSession.objects.create(profil=self.aicha, cursus=self.cursus, mode=ModeQuiz.PRATIQUE)
        QuizAnswer.objects.create(
            quiz_question=QuizQuestion.objects.create(session=session, question=ancienne, ordre=1),
            resultat_declare="REUSSI",
        )
        stats, _, _ = progression_par_theme(self.aicha, self.cursus)
        self.assertEqual(dict(stats), {})


@override_settings(PARCOURS_CONTENU_CACHE_SECONDES=600, CACHES=CACHE_DE_TEST)
class CacheDuSqueletteTests(ParcoursFixture):
    def setUp(self):
        super().setUp()
        caches["parcours"].clear()

    def test_le_second_appel_ne_relit_que_la_progression(self):
        with CaptureQueriesContext(connection) as premier:
            avant = construire_parcours_par_frequence(self.aicha, self.cursus, self.subject)
        with CaptureQueriesContext(connection) as second:
            apres = construire_parcours_par_frequence(self.aicha, self.cursus, self.subject)
        self.assertEqual(avant, apres)
        # Réponses de quiz, QCM des copies d'examen (inédites puis annales), révisions, lectures : cinq requêtes, plus aucune
        # sur le contenu.
        self.assertEqual(len(second), 5)
        self.assertGreater(len(premier), len(second))

    def test_la_progression_d_un_eleve_n_est_jamais_servie_a_un_autre(self):
        self._repondre(self.aicha)
        self.assertEqual(self._theme(self.aicha, self.frequent.name)["taux"], 100)
        # Le squelette est maintenant en cache : Bruno, qui n'a rien fait, ne doit rien hériter d'Aïcha.
        theme = self._theme(self.bruno, self.frequent.name)
        self.assertIsNone(theme["taux"])
        self.assertEqual(theme["nb_reponses"], 0)
        # Et ce que Bruno fait ensuite se voit tout de suite, cache ou pas.
        self._repondre(self.bruno, correcte=False)
        self.assertEqual(self._theme(self.bruno, self.frequent.name)["taux"], 0)

    def test_un_contenu_publie_apparait_des_que_le_cache_est_vide(self):
        construire_parcours_par_frequence(self.aicha, self.cursus, self.subject)
        nouveau = Tag.objects.create(name="nouveau (test cache)")
        for i in range(3):
            _make_lesson_avec_themes(self.subject, self.cursus, f"Lesson de plus {i}", [[nouveau]])
        noms = lambda: [t["intitule"] for t in construire_parcours_par_frequence(self.aicha, self.cursus, self.subject)]
        # Tant que le cache tient, le classement est celui d'avant : c'est le prix accepté.
        self.assertNotIn(nouveau.name, noms())
        # L'application d'un lot le vide (voir synchro.moteur).
        oublier_squelettes()
        self.assertIn(nouveau.name, noms())

    def test_modifier_le_resultat_n_abime_pas_la_copie_partagee(self):
        themes = construire_parcours_par_frequence(self.aicha, self.cursus, self.subject)
        themes[0]["intitule"] = "abîmé"
        themes[0]["cours"].append({"slug": "intrus"})
        encore = construire_parcours_par_frequence(self.aicha, self.cursus, self.subject)
        self.assertEqual(encore[0]["intitule"], self.frequent.name)
        self.assertEqual(encore[0]["cours"], [])

    def test_le_resume_est_le_meme_avec_et_sans_cache(self):
        self._repondre(self.aicha)
        avec = resume_parcours(self.aicha, self.cursus)
        encore = resume_parcours(self.aicha, self.cursus)
        with override_settings(PARCOURS_CONTENU_CACHE_SECONDES=0):
            sans = resume_parcours(self.aicha, self.cursus)
        self.assertEqual(avec, sans)
        self.assertEqual(avec, encore)
        ligne = next(r for r in avec if r["subject_id"] == self.subject.id)
        self.assertEqual(ligne["total"], 2)

    def test_un_corpus_trop_mince_est_retenu_lui_aussi(self):
        autre = Subject.objects.create(code="TEST_CACHE_VIDE", label="Vide (test cache)", country=self.cursus.country)
        self.assertIsNone(construire_parcours_par_frequence(self.aicha, self.cursus, autre))
        with CaptureQueriesContext(connection) as second:
            self.assertIsNone(construire_parcours_par_frequence(self.aicha, self.cursus, autre))
        self.assertEqual(len(second), 0)
