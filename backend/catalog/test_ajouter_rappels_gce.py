"""
Commande ajouter_rappels_gce : rappels de méthode des Paper 2 du GCE + cours gratuit par matière.

Les corrigés GCE sont rédigés à l'ingestion, sans RappelDeMethode ; les cours, eux, existent par
thème. La commande pose, dans le corrigé d'une question de chaque exercice de Paper 2, un bloc
« ### Rappel de méthode » tiré du cours du thème (ses premiers points à retenir : une règle générale,
jamais la réponse) et le trace par un RappelDeMethode relié à ce cours - le « Voir le cours complet »
du corrigé. Sur une épreuve gratuite, seul le cours gratuit de la matière reste relié, car un cours
est gratuit dès qu'un de ses rappels vient d'une épreuve gratuite.
"""
import json
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase

from .ingestion import _resolve_cursus_list, ingest_exercise
from .models import Cours, RappelDeMethode, StatutContenu, Tag
from .rendering import lesson_exercises_breakdown

FIXTURES = Path(__file__).parent / "fixtures_gce"

SYNTHESE = [
    "Premier point a retenir.",
    "Deuxieme point a retenir.",
    "Troisieme point a retenir.",
    "Quatrieme point jamais repris.",
]


def _ingerer(nom):
    data = json.loads((FIXTURES / nom).read_text(encoding="utf-8"))
    return ingest_exercise(data, source_dir=Path("ingest/cm") / nom.removesuffix(".json"), exiger_themes=True)[0]


def _paragraphe(titre):
    """Le paragraphe attendu pour le cours `titre` : ses 3 premiers points, préfixés de son titre (textes distincts par cours)."""
    return " ".join(f"{titre}: {p}" for p in SYNTHESE[:3])


def _cours(exercice, theme, titre):
    cours = Cours.objects.create(
        external_id=f"cours-test-{titre}", titre=titre, subject=exercice.lesson.subject,
        statut=StatutContenu.VALIDE, content_markdown="Contenu.",
        sections_raw=[{"type": "accroche", "contenu_markdown": "Accroche."},
                      {"type": "synthese", "items_markdown": [f"{titre}: {p}" for p in SYNTHESE]}],
    )
    cours.cursus.set(exercice.lesson.cursus.all())
    cours.tags.add(Tag.objects.get(name=theme))
    return cours


def _lancer(*args):
    sortie = StringIO()
    call_command("ajouter_rappels_gce", *args, stdout=sortie)
    return sortie.getvalue()


class _Base(TestCase):
    def setUp(self):
        _resolve_cursus_list.cache_clear()
        # Paper 2, 3 questions : a « simultaneous equations » + « forming equations », b et c « simultaneous equations ».
        # « forming equations » (1 question) est plus spécifique que « simultaneous equations » (3).
        self.exercice = _ingerer("gce_ol_maths_2019_p2_a3.json")
        self.themes = ["forming equations", "simultaneous equations"]  # du plus spécifique au plus général
        self.cours = [_cours(self.exercice, t, f"Cours {t}") for t in self.themes]
        self.questions = list(self.exercice.questions.order_by("ordre"))

    def tearDown(self):
        _resolve_cursus_list.cache_clear()


class RappelsPaper2Tests(_Base):
    def test_simulation_n_ecrit_rien(self):
        sortie = _lancer()

        self.assertEqual(RappelDeMethode.objects.count(), 0)
        self.assertNotIn("Rappel de méthode", self.questions[0].corrige_markdown)
        self.assertIn("simulation", sortie)

    def test_un_rappel_par_theme_relie_au_cours_et_ecrit_dans_le_corrige(self):
        _lancer("--appliquer")

        rappels = RappelDeMethode.objects.filter(exercise=self.exercice)
        self.assertEqual(rappels.count(), 2)
        self.assertEqual({r.cours_id for r in rappels}, {c.pk for c in self.cours})
        # Un rappel par thème, posé sur la première question dont CE thème est le plus spécifique.
        for question, theme in ((self.questions[0], "forming equations"), (self.questions[1], "simultaneous equations")):
            question.refresh_from_db()
            self.assertTrue(question.corrige_markdown.startswith("### Rappel de méthode"), theme)
            self.assertIn(_paragraphe(f"Cours {theme}"), question.corrige_markdown)
            self.assertNotIn("Quatrieme", question.corrige_markdown)
        self.questions[2].refresh_from_db()
        self.assertNotIn("Rappel de méthode", self.questions[2].corrige_markdown)
        self.assertEqual({r.competence for r in rappels}, set(self.themes))
        for r in rappels:
            self.assertEqual(r.contenu_markdown, _paragraphe(f"Cours {r.competence}"))

    def test_le_corrige_lu_porte_le_lien_du_cours_sous_le_rappel(self):
        _lancer("--appliquer")

        corrige = lesson_exercises_breakdown(self.exercice.lesson)[0]["corrige_markdown"]

        for c in self.cours:
            # Le lien suit immédiatement le bloc du rappel qui mène à ce cours.
            self.assertIn(f"### Rappel de méthode\n\n{_paragraphe(c.titre)}\n\n[COURS_LINK:{c.slug}]", corrige)
        # La question c (sans rappel) reçoit, elle, le lien de son thème - sans second lien sous les rappels.
        self.assertEqual(corrige.count(f"[COURS_LINK:{self.cours[0].slug}]"), 1)
        self.assertEqual(corrige.count(f"[COURS_LINK:{self.cours[1].slug}]"), 2)

    def test_relancer_ne_duplique_rien(self):
        _lancer("--appliquer")
        corriges_1 = [q.corrige_markdown for q in self.exercice.questions.order_by("ordre")]
        _lancer("--appliquer")

        self.assertEqual(RappelDeMethode.objects.filter(exercise=self.exercice).count(), 2)
        self.assertEqual([q.corrige_markdown for q in self.exercice.questions.order_by("ordre")], corriges_1)

    def test_theme_sans_cours_ne_donne_pas_de_rappel(self):
        self.cours[0].statut = StatutContenu.BROUILLON  # « forming equations » : plus de cours publié
        self.cours[0].save()

        _lancer("--appliquer")

        # La question a retombe sur son autre thème, « simultaneous equations » : un seul rappel.
        rappels = RappelDeMethode.objects.filter(exercise=self.exercice)
        self.assertEqual([r.competence for r in rappels], ["simultaneous equations"])

    def test_le_paper_1_n_est_pas_touche(self):
        p1 = _ingerer("gce_ol_maths_2019_p1_ex1.json")
        theme = p1.questions.first().themes.first().name
        _cours(p1, theme, "Cours p1")

        _lancer("--appliquer")

        self.assertEqual(RappelDeMethode.objects.filter(exercise=p1).count(), 0)


class CoursGratuitsTests(_Base):
    """
    Un cours cité par une épreuve gratuite est gratuit (règle produit : Cours.est_vitrine). Sur une épreuve gratuite,
    chaque cours que le lecteur propose sous une question reçoit donc un rappel de méthode qui y mène.
    """

    def _vitrine(self, exercice):
        exercice.lesson.est_vitrine = True
        exercice.lesson.save()

    def _gratuit(self, cours):
        return Cours.objects.get(pk=cours.pk).est_vitrine

    def test_paper_2_gratuit_tous_ses_rappels_sont_relies_et_ses_cours_gratuits(self):
        self._vitrine(self.exercice)

        _lancer("--appliquer")

        rappels = RappelDeMethode.objects.filter(exercise=self.exercice)
        self.assertEqual({r.cours_id for r in rappels}, {c.pk for c in self.cours})
        for c in self.cours:
            self.assertTrue(self._gratuit(c), c.titre)

    def test_une_epreuve_payante_n_ouvre_aucun_cours(self):
        _lancer("--appliquer")

        for c in self.cours:
            self.assertFalse(self._gratuit(c), c.titre)

    def test_des_rappels_deja_crees_sans_cours_sont_relies_au_rejeu(self):
        _lancer("--appliquer")
        RappelDeMethode.objects.filter(exercise=self.exercice).update(cours=None)  # état d'avant : rappels non reliés
        self._vitrine(self.exercice)

        _lancer("--appliquer")

        self.assertEqual({r.cours_id for r in RappelDeMethode.objects.filter(exercise=self.exercice)}, {c.pk for c in self.cours})
        self.assertTrue(all(self._gratuit(c) for c in self.cours))


class CoursGratuitsPaper1Tests(_Base):
    """Paper 1 gratuit (50 QCM, un seul exercice) : un rappel par cours que le lecteur propose sous ses questions."""

    def setUp(self):
        super().setUp()
        # Q1 [order of operations, fractions], Q2 [place value, decimals], Q3 [inequalities], Q4 [fractions, addition of fractions],
        # Q5 [standard form, indices], Q6 [significant figures, rounding]. Un QCM n'a qu'UN cours : son thème le plus spécifique.
        self.p1 = _ingerer("gce_ol_maths_2019_p1_ex1.json")
        self.lies = {t: _cours(self.p1, t, f"Cours {t}") for t in ("order of operations", "place value", "inequalities", "fractions")}
        # Cité nulle part dans l'épreuve : ne doit pas devenir gratuit.
        Tag.objects.create(name="algebra")
        self.etranger = _cours(self.p1, "algebra", "Cours etranger")

    def _gratuit(self, cours):
        return Cours.objects.get(pk=cours.pk).est_vitrine

    def test_chaque_cours_cite_par_l_epreuve_gratuite_devient_gratuit(self):
        self.p1.lesson.est_vitrine = True
        self.p1.lesson.save()

        _lancer("--appliquer")

        rappels = RappelDeMethode.objects.filter(exercise=self.p1)
        self.assertEqual({r.cours_id for r in rappels}, {c.pk for c in self.lies.values()})
        self.assertEqual(rappels.count(), len(self.lies))
        for theme, cours in self.lies.items():
            self.assertTrue(self._gratuit(cours), theme)
        self.assertFalse(self._gratuit(self.etranger))

    def test_le_rappel_est_ecrit_sous_la_premiere_question_qui_cite_le_cours(self):
        self.p1.lesson.est_vitrine = True
        self.p1.lesson.save()

        _lancer("--appliquer")

        questions = list(self.p1.questions.order_by("ordre"))
        self.assertTrue(questions[2].corrige_markdown.startswith("### Rappel de méthode"))  # Q3 : inequalities
        rappel = RappelDeMethode.objects.get(exercise=self.p1, competence="inequalities")
        self.assertIn(rappel.contenu_markdown, questions[2].corrige_markdown)

    def test_relancer_ne_duplique_rien(self):
        self.p1.lesson.est_vitrine = True
        self.p1.lesson.save()
        _lancer("--appliquer")
        corriges = [q.corrige_markdown for q in self.p1.questions.order_by("ordre")]

        _lancer("--appliquer")

        self.assertEqual(RappelDeMethode.objects.filter(exercise=self.p1).count(), len(self.lies))
        self.assertEqual([q.corrige_markdown for q in self.p1.questions.order_by("ordre")], corriges)

    def test_epreuve_payante_de_paper_1_ne_donne_aucun_rappel(self):
        _lancer("--appliquer")

        self.assertEqual(RappelDeMethode.objects.filter(exercise=self.p1).count(), 0)
        for cours in self.lies.values():
            self.assertFalse(self._gratuit(cours))
