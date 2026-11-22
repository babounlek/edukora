"""La Fiche et la Correction d'un quiz nomment la matière, même quand la session n'en porte pas (quiz lancé depuis un thème)."""
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from catalog.models import Cursus, Examen, Subject, Tag
from users.models import User

from . import instantane
from .models import ModeQuiz, QuizQuestion, QuizSession
from .pdf import _combined_markdown, _corrige_deep_link, _render_html, _sujet_deep_link, matieres_de_la_session
from .tests import _make_competence_item


class _Base(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677610011", password="x")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.maths = Subject.objects.get(country__code="CM", code="MATHS")
        self.autres = list(Subject.objects.filter(country__code="CM", langue="fr").exclude(pk=self.maths.pk)[:3])
        self.theme = Tag.objects.create(name="identité remarquable")

    def _session(self, **kwargs):
        return QuizSession.objects.create(
            profil=self.user.profils.first(), cursus=self.cursus, mode=ModeQuiz.PRATIQUE, **kwargs,
        )

    def _question(self, session, ordre, matiere, *, fige=True):
        item = _make_competence_item(matiere, self.cursus, theme=self.theme, numero=f"m{session.pk}-{ordre}")
        item = type(item).objects.select_related("theme", "subject").get(pk=item.pk)
        return QuizQuestion.objects.create(
            session=session, competence_item=item, ordre=ordre, snapshot=instantane.figer_item(item) if fige else None,
        )

    def _fiche(self, session):
        return _render_html(
            session, avec_corrige=False, template_name="quiz/fiche_sujet_pdf_template.html",
            deep_link=_sujet_deep_link(session),
        )

    def _correction(self, session):
        return _render_html(
            session, avec_corrige=True, template_name="quiz/fiche_corrige_pdf_template.html",
            deep_link=_corrige_deep_link(session),
        )


class MatiereDeLaFicheDeQuizTests(_Base):
    def test_un_quiz_lance_depuis_un_theme_nomme_la_matiere_de_ses_questions(self):
        session = self._session(theme=self.theme)  # pas de matière sur la session : le cas qui sortait sans titre
        self._question(session, 1, self.maths)
        self._question(session, 2, self.maths)

        for html in (self._fiche(session), self._correction(session)):
            self.assertIn(f"<h1>{self.maths.label}</h1>", html)
            self.assertIn(f" - {self.maths.label}</title>", html)

    def test_une_seule_matiere_ne_se_repete_pas_sur_chaque_question(self):
        session = self._session(theme=self.theme)
        self._question(session, 1, self.maths)
        self._question(session, 2, self.maths)

        md = _combined_markdown(session, avec_corrige=False)

        self.assertIn("## Question 1\n", md)
        self.assertNotIn(f"Question 1 - {self.maths.label}", md)

    def test_la_matiere_choisie_au_lancement_reste_le_titre(self):
        session = self._session(subject=self.maths)
        self._question(session, 1, self.maths)

        self.assertEqual(matieres_de_la_session(session), [self.maths.label])
        self.assertIn(f"<h1>{self.maths.label}</h1>", self._fiche(session))

    def test_un_quiz_mele_nomme_ses_matieres_dans_lordre_et_sur_chaque_question(self):
        session = self._session()
        autre = self.autres[0]
        self._question(session, 1, autre)
        self._question(session, 2, self.maths)
        self._question(session, 3, autre)

        self.assertEqual(matieres_de_la_session(session), [autre.label, self.maths.label])
        html = self._fiche(session)
        self.assertIn(f"<h1>{autre.label} · {self.maths.label}</h1>", html)
        for md in (_combined_markdown(session, avec_corrige=False), _combined_markdown(session, avec_corrige=True)):
            self.assertIn(f"## Question 1 - {autre.label}", md)
            self.assertIn(f"## Question 2 - {self.maths.label}", md)
            self.assertIn(f"## Question 3 - {autre.label}", md)

    def test_au_dela_de_trois_matieres_le_titre_dit_plusieurs_matieres(self):
        session = self._session()
        for ordre, matiere in enumerate([self.maths, *self.autres], start=1):
            self._question(session, ordre, matiere)

        html = self._fiche(session)

        self.assertIn("<h1>Plusieurs matières</h1>", html)
        self.assertIn(f"Question 1 - {self.maths.label}", html)

    def test_la_matiere_est_celle_de_linstantane_a_defaut_du_contenu_vivant(self):
        session = self._session(theme=self.theme)
        figee = self._question(session, 1, self.maths)
        figee.competence_item.subject = self.autres[0]  # reclassé après coup : la fiche garde ce que l'élève a vu
        figee.competence_item.save()
        self.assertEqual(matieres_de_la_session(session), [self.maths.label])

        vivante = self._session(theme=self.theme)
        self._question(vivante, 1, self.maths, fige=False)
        self.assertEqual(matieres_de_la_session(vivante), [self.maths.label])


class RefairePdfQuizSansMatiereTests(_Base):
    def _avec_pdf(self, **kwargs):
        session = self._session(sujet_pdf="cm/1/ancien-fiche.pdf", **kwargs)
        self._question(session, 1, self.maths)
        return session

    def _lancer(self, *args):
        sortie = StringIO()
        call_command("refaire_pdf_quiz_sans_matiere", *args, stdout=sortie)
        return sortie.getvalue()

    @patch("quiz.management.commands.refaire_pdf_quiz_sans_matiere.save_quiz_fiche_pdfs")
    def test_refait_les_pdf_des_sessions_sans_matiere_et_seulement_eux(self, refaire):
        sans_matiere = self._avec_pdf(theme=self.theme)
        self._avec_pdf(subject=self.maths)          # titre déjà juste
        jamais_generee = self._session(theme=self.theme)  # sortira juste à la demande
        self._question(jamais_generee, 1, self.maths)

        sortie = self._lancer()

        self.assertEqual([appel.args[0].pk for appel in refaire.call_args_list], [sans_matiere.pk])
        self.assertIn("Sessions : 1 refaite(s) sur 1, 0 échec(s).", sortie)

    @patch("quiz.management.commands.refaire_pdf_quiz_sans_matiere.save_quiz_fiche_pdfs")
    def test_simuler_compte_sans_rien_generer(self, refaire):
        self._avec_pdf(theme=self.theme)

        sortie = self._lancer("--simuler")

        refaire.assert_not_called()
        self.assertIn("Sessions à refaire : 1", sortie)

    @patch("quiz.management.commands.refaire_pdf_quiz_sans_matiere.save_quiz_fiche_pdfs")
    def test_un_echec_ne_bloque_pas_les_suivantes(self, refaire):
        premiere = self._avec_pdf(theme=self.theme)
        self._avec_pdf(theme=self.theme)
        refaire.side_effect = [RuntimeError("Chromium absent"), None]

        sortie = self._lancer()

        self.assertEqual(refaire.call_count, 2)
        self.assertIn(f"Session #{premiere.pk} : échec, ancien PDF conservé", sortie)
        self.assertIn("Sessions : 1 refaite(s) sur 2, 1 échec(s).", sortie)
