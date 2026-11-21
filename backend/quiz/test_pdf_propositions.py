"""Les PDF Fiche et Correction d'une session de quiz impriment les propositions des QCM (quiz.pdf._combined_markdown)."""
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from catalog.models import Cursus, Examen, Subject, Tag, TypeReponse
from users.models import User

from . import instantane
from .models import ModeQuiz, QuizQuestion, QuizSession
from .pdf import _combined_markdown
from .tests import _make_competence_item

CHOIX = [
    {"lettre": "a", "texte": "Un navigateur"},
    {"lettre": "b", "texte": "Un antivirus"},
    {"lettre": "c", "texte": "Un traitement de texte"},
    {"lettre": "d", "texte": "Un système d'exploitation"},
]


class PropositionsDansLesPdfDuQuizTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677610001", password="x")
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.theme = Tag.objects.create(name="logiciels")
        self.session = QuizSession.objects.create(
            profil=self.user.profils.first(), cursus=self.cursus, mode=ModeQuiz.PRATIQUE,
        )

    def _question(self, ordre, *, fige=True, enonce_markdown, corrige_markdown, **kwargs):
        item = _make_competence_item(self.subject, self.cursus, theme=self.theme, numero=f"p{ordre}", **kwargs)
        # La fixture écrit ses propres textes : on pose les nôtres ensuite.
        type(item).objects.filter(pk=item.pk).update(enonce_markdown=enonce_markdown, corrige_markdown=corrige_markdown)
        item = type(item).objects.select_related("theme", "subject").get(pk=item.pk)
        return QuizQuestion.objects.create(
            session=self.session, competence_item=item, ordre=ordre,
            snapshot=instantane.figer_item(item) if fige else None,
        )

    def _qcm(self, ordre, **kwargs):
        kwargs.setdefault("enonce_markdown", "Quel logiciel installer en premier ?")
        kwargs.setdefault("corrige_markdown", "### Corrigé\n\nSans lui, rien ne démarre.")
        return self._question(
            ordre, type_reponse=TypeReponse.QCM, choix=CHOIX, reponse_correcte="d", **kwargs,
        )

    def test_la_fiche_imprime_les_propositions_sous_lenonce(self):
        self._qcm(1)

        md = _combined_markdown(self.session, avec_corrige=False)

        self.assertLess(md.index("Quel logiciel installer en premier ?"), md.index("**A.** Un navigateur"))
        for lettre, texte in zip("ABCD", (c["texte"] for c in CHOIX)):
            self.assertIn(f"**{lettre}.** {texte}", md)

    def test_la_fiche_ne_donne_pas_la_bonne_reponse(self):
        self._qcm(1)

        md = _combined_markdown(self.session, avec_corrige=False)

        self.assertNotIn("Bonne réponse", md)
        self.assertNotIn("Sans lui, rien ne démarre.", md)

    def test_la_fiche_laisse_les_quatre_cases_vides(self):
        self._qcm(1)

        md = _combined_markdown(self.session, avec_corrige=False)

        self.assertEqual(md.count("<span class='case'></span>"), 4)
        self.assertNotIn("cochee", md)  # une case cochée sur la fiche donnerait la réponse

    def test_la_correction_coche_la_seule_case_de_la_bonne_reponse(self):
        self._qcm(1)

        md = _combined_markdown(self.session, avec_corrige=True)

        self.assertEqual(md.count("cochee"), 1)
        self.assertIn("<span class='case cochee'></span>**D.**", md)

    def test_la_correction_reprend_les_propositions_puis_nomme_la_bonne_lettre_avant_le_corrige(self):
        self._qcm(1)

        md = _combined_markdown(self.session, avec_corrige=True)

        self.assertLess(md.index("**D.** Un système d'exploitation"), md.index("**Bonne réponse : D**"))
        self.assertLess(md.index("**Bonne réponse : D**"), md.index("### Corrigé"))

    def test_une_question_ouverte_reste_sans_proposition_ni_bonne_reponse(self):
        self._question(1, enonce_markdown="Dériver $x^2$.", corrige_markdown="### Corrigé\n\n$2x$.")

        md = _combined_markdown(self.session, avec_corrige=True)

        self.assertNotIn("propositions", md)
        self.assertNotIn("Bonne réponse", md)

    def test_les_propositions_sont_celles_de_linstantane_pas_celles_du_contenu_vivant(self):
        quiz_question = self._qcm(1)
        vivant = quiz_question.competence_item
        vivant.choix = [{"lettre": "a", "texte": "Réécrit après coup"}, {"lettre": "b", "texte": "Autre"}]
        vivant.reponse_correcte = "a"
        vivant.save()

        md = _combined_markdown(self.session, avec_corrige=True)

        self.assertIn("**D.** Un système d'exploitation", md)
        self.assertNotIn("Réécrit après coup", md)
        self.assertIn("**Bonne réponse : D**", md)

    def test_une_question_sans_instantane_prend_les_propositions_du_contenu_vivant(self):
        self._qcm(1, fige=False)

        md = _combined_markdown(self.session, avec_corrige=True)

        self.assertIn("**A.** Un navigateur", md)
        self.assertIn("**Bonne réponse : D**", md)

    def test_chaque_question_garde_ses_propres_propositions(self):
        self._qcm(1)
        self._question(2, enonce_markdown="Dériver $x^2$.", corrige_markdown="### Corrigé\n\n$2x$.")

        md = _combined_markdown(self.session, avec_corrige=False)

        self.assertLess(md.index("**D.** Un système d'exploitation"), md.index("## Question 2"))
        self.assertEqual(md.count("**A.** "), 1)


class RefairePdfQcmTests(TestCase):
    """La commande refaire_pdf_qcm : seuls les PDF déjà générés qui contiennent une QCM sont refaits."""

    def setUp(self):
        self.user = User.objects.create_user(phone_number="677610002", password="x")
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.theme = Tag.objects.create(name="logiciels")

    def _session(self, *, avec_pdf, qcm, fige=True):
        session = QuizSession.objects.create(
            profil=self.user.profils.first(), cursus=self.cursus, mode=ModeQuiz.PRATIQUE,
            sujet_pdf="cm/1/ancien-fiche.pdf" if avec_pdf else "",
        )
        kwargs = {"type_reponse": TypeReponse.QCM, "choix": CHOIX, "reponse_correcte": "d"} if qcm else {}
        item = _make_competence_item(self.subject, self.cursus, theme=self.theme, numero=f"s{session.pk}", **kwargs)
        item = type(item).objects.select_related("theme", "subject").get(pk=item.pk)
        QuizQuestion.objects.create(
            session=session, competence_item=item, ordre=1, snapshot=instantane.figer_item(item) if fige else None,
        )
        return session

    def _lancer(self, *args):
        sortie = StringIO()
        call_command("refaire_pdf_qcm", *args, stdout=sortie)
        return sortie.getvalue()

    @patch("quiz.management.commands.refaire_pdf_qcm.save_quiz_fiche_pdfs")
    def test_refait_les_sessions_qui_ont_un_pdf_et_une_qcm_et_seulement_elles(self, refaire):
        figee = self._session(avec_pdf=True, qcm=True)
        vivante = self._session(avec_pdf=True, qcm=True, fige=False)
        self._session(avec_pdf=True, qcm=False)   # rien à corriger : aucune proposition
        self._session(avec_pdf=False, qcm=True)   # jamais générée : sortira juste à la demande

        sortie = self._lancer()

        self.assertEqual([appel.args[0].pk for appel in refaire.call_args_list], [figee.pk, vivante.pk])
        self.assertIn("Sessions : 2 refait(s) sur 2, 0 échec(s).", sortie)

    @patch("quiz.management.commands.refaire_pdf_qcm.save_quiz_fiche_pdfs")
    def test_simuler_compte_sans_rien_generer(self, refaire):
        self._session(avec_pdf=True, qcm=True)

        sortie = self._lancer("--simuler")

        refaire.assert_not_called()
        self.assertIn("Sessions à refaire : 1", sortie)
        self.assertIn("Fiches à refaire : 0", sortie)

    @patch("quiz.management.commands.refaire_pdf_qcm.save_quiz_fiche_pdfs")
    def test_un_echec_ne_bloque_pas_les_suivantes(self, refaire):
        premiere = self._session(avec_pdf=True, qcm=True)
        self._session(avec_pdf=True, qcm=True)
        refaire.side_effect = [RuntimeError("Chromium absent"), None]

        sortie = self._lancer()

        self.assertEqual(refaire.call_count, 2)
        self.assertIn(f"Session #{premiere.pk} : échec, ancien PDF conservé", sortie)
        self.assertIn("Sessions : 1 refait(s) sur 2, 1 échec(s).", sortie)
        premiere.refresh_from_db()
        self.assertEqual(premiere.sujet_pdf.name, "cm/1/ancien-fiche.pdf")
