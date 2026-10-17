"""
Liens « Voir le cours complet » par THÈME sous les questions d'une épreuve GCE.

Les corrigés GCE n'ont aucun RappelDeMethode (les sujets n'avaient pas de corrigé, il a été rédigé à
l'ingestion) : sans eux, l'épreuve n'avait aucun pont vers les cours. Chaque question porte pourtant
ses thèmes, et chaque thème a un cours (même Tag) : le lecteur ajoute donc, sous chaque question, un
marqueur `[COURS_LINK:<slug>]` vers le cours publié de son thème. Réservé aux examens GCE : le corpus
francophone, lui, passe par ses rappels.
"""
import json
from pathlib import Path

from django.test import TestCase

from .ingestion import _resolve_cursus_list, ingest_exercise
from .models import Cours, Cursus, Examen, RappelDeMethode, StatutContenu, Subject, Tag
from .rendering import exercise_questions_breakdown, lesson_exercises_breakdown

FIXTURES = Path(__file__).parent / "fixtures_gce"


def _ingerer(nom):
    data = json.loads((FIXTURES / nom).read_text(encoding="utf-8"))
    dossier = Path("ingest/cm") / nom.removesuffix(".json")
    return ingest_exercise(data, source_dir=dossier, exiger_themes=True)[0]


def _cours(exercice, theme, titre, **extra):
    """Cours VALIDE du cursus de l'épreuve, étiqueté par le Tag `theme`."""
    cours = Cours.objects.create(
        external_id=f"cours-test-{titre}", titre=titre, subject=exercice.lesson.subject,
        statut=extra.pop("statut", StatutContenu.VALIDE),
        content_markdown=extra.pop("content_markdown", "Contenu du cours."), **extra,
    )
    cours.cursus.set(exercice.lesson.cursus.all())
    cours.tags.add(Tag.objects.get(name=theme))
    return cours


class _Base(TestCase):
    def setUp(self):
        _resolve_cursus_list.cache_clear()

    def tearDown(self):
        _resolve_cursus_list.cache_clear()


class CoursParThemeTests(_Base):
    def _corriges(self, exercice):
        return lesson_exercises_breakdown(exercice.lesson)[0]["corrige_markdown"]

    def test_la_question_porte_le_lien_du_cours_de_son_theme(self):
        exercice = _ingerer("gce_ol_maths_2019_p1_ex1.json")
        theme = exercice.questions.order_by("ordre").first().themes.first().name
        cours = _cours(exercice, theme, "Cours du theme")

        corrige = self._corriges(exercice)

        self.assertIn(f"[COURS_LINK:{cours.slug}]", corrige)

    def test_le_lien_suit_la_question_qui_porte_le_theme(self):
        exercice = _ingerer("gce_ol_maths_2019_p1_ex1.json")
        questions = list(exercice.questions.order_by("ordre"))
        # Le thème propre à la première question seulement : le marqueur doit être avant le corrigé de la 2e.
        themes_suivants = {t.pk for q in questions[1:] for t in q.themes.all()}
        propre = next((t for t in questions[0].themes.all() if t.pk not in themes_suivants), None)
        self.assertIsNotNone(propre, "la fixture doit avoir un thème propre à la question 1")
        cours = _cours(exercice, propre.name, "Cours question un")

        corrige = self._corriges(exercice)
        position_lien = corrige.index(f"[COURS_LINK:{cours.slug}]")
        debut_question_2 = corrige.index(questions[1].corrige_markdown[:40])

        self.assertLess(position_lien, debut_question_2)
        self.assertEqual(corrige.count(f"[COURS_LINK:{cours.slug}]"), 1)

    def test_cours_brouillon_ou_vide_ou_d_une_autre_matiere_jamais_lie(self):
        exercice = _ingerer("gce_ol_maths_2019_p1_ex1.json")
        theme = exercice.questions.order_by("ordre").first().themes.first().name
        brouillon = _cours(exercice, theme, "Brouillon", statut=StatutContenu.BROUILLON)
        vide = _cours(exercice, theme, "Vide", content_markdown="")
        autre_matiere = _cours(exercice, theme, "Autre matiere")
        autre_matiere.subject = Subject.objects.get(code="GCE_PHYSICS")
        autre_matiere.save()

        corrige = self._corriges(exercice)

        for cours in (brouillon, vide, autre_matiere):
            self.assertNotIn(f"[COURS_LINK:{cours.slug}]", corrige)

    def test_cours_d_un_autre_cursus_jamais_lie(self):
        exercice = _ingerer("gce_ol_maths_2019_p1_ex1.json")
        theme = exercice.questions.order_by("ordre").first().themes.first().name
        cours = _cours(exercice, theme, "Autre cursus")
        autre = Cursus.objects.filter(examen=Examen.GCE_AL).first() or Cursus.objects.exclude(
            pk__in=exercice.lesson.cursus.values("pk"),
        ).first()
        cours.cursus.set([autre])

        self.assertNotIn(f"[COURS_LINK:{cours.slug}]", self._corriges(exercice))

    def test_au_plus_deux_cours_par_question(self):
        exercice = _ingerer("gce_ol_maths_2019_p2_a1.json")  # la question 1 porte deux thèmes
        question = exercice.questions.order_by("ordre").first()
        slugs = [_cours(exercice, t.name, f"Cours {t.name}").slug for t in question.themes.all()]
        self.assertEqual(len(slugs), 2)

        corrige = self._corriges(exercice)

        for slug in slugs:
            self.assertIn(f"[COURS_LINK:{slug}]", corrige)

    def test_question_sans_cours_reste_inchangee(self):
        exercice = _ingerer("gce_ol_maths_2019_p1_ex1.json")
        avant = self._corriges(exercice)
        self.assertNotIn("COURS_LINK", avant)

    def test_aucun_lien_de_theme_sur_une_question_deja_liee_par_un_rappel(self):
        exercice = _ingerer("gce_ol_maths_2019_p2_a1.json")
        question = exercice.questions.order_by("ordre").first()
        theme = question.themes.first().name
        cours_rappel = _cours(exercice, theme, "Cours du rappel")
        question.corrige_markdown = f"### Rappel de méthode\n\nUne règle de méthode.\n\n{question.corrige_markdown}"
        question.save()
        exercice.compile_from_questions()
        RappelDeMethode.objects.create(
            exercise=exercice, external_id="rdm-test-1", competence=theme,
            contenu_markdown="Une règle de méthode.", cours=cours_rappel,
        )

        corrige = self._corriges(exercice)

        self.assertEqual(corrige.count(f"[COURS_LINK:{cours_rappel.slug}]"), 1)

    def test_la_lecture_d_un_exercice_isole_porte_les_memes_liens(self):
        exercice = _ingerer("gce_ol_maths_2019_p1_ex1.json")
        theme = exercice.questions.order_by("ordre").first().themes.first().name
        cours = _cours(exercice, theme, "Cours exercice isole")

        par_question = exercise_questions_breakdown(exercice)

        self.assertTrue(any(f"[COURS_LINK:{cours.slug}]" in q["corrige_markdown"] for q in par_question))

    def test_un_qcm_n_a_qu_un_cours_le_plus_specifique(self):
        # Q1 « order of operations / fractions » (QCM) : « order of operations » n'apparaît qu'une fois,
        # « fractions » deux fois (Q1 et Q4) -> seul le cours le plus spécifique est lié à Q1.
        exercice = _ingerer("gce_ol_maths_2019_p1_ex1.json")
        specifique = _cours(exercice, "order of operations", "Cours specifique")
        general = _cours(exercice, "fractions", "Cours general")

        corrige = self._corriges(exercice)
        avant_q2 = corrige[: corrige.index("**2.**")]

        self.assertIn(f"[COURS_LINK:{specifique.slug}]", avant_q2)
        self.assertNotIn(f"[COURS_LINK:{general.slug}]", avant_q2)
        # Le cours général reste lié là où il est le plus spécifique (Q4).
        self.assertEqual(corrige.count(f"[COURS_LINK:{general.slug}]"), 1)

