"""
Couvre les deux risques principaux du module : la sélection d'items (voir
quiz.services.generer_session) et la fuite de la bonne réponse avant que l'élève n'ait
répondu (voir quiz.views._question_payload) - un test de niveau ou un quiz dont la
réponse est visible dans l'onglet réseau avant d'être tentée ne vaut rien.

generer_session pioche exclusivement dans CompetenceItem depuis la bascule (voir
quiz.services._items_eligibles) : un item est rédigé dès l'origine pour se suffire
seul, contrairement à une catalog.Question qui reste un extrait fidèle d'une épreuve
réelle, pensé pour être lu dans le récit complet de son Exercise. catalog.Question
n'est donc plus jamais tirée pour une nouvelle session - _make_question et les
fixtures qui en dépendent (QuizQuestionDeletionTests, LegacyQuestionPayloadTests) ne
couvrent plus que la lecture d'un historique de sessions créées avant la bascule.
"""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import (
    Country, Cursus, Difficulte, Examen, Exercise, Lesson, LessonType, Question, Series, StatutContenu, Subject, Tag,
    TypeReponse,
)
from subscriptions.models import Subscription
from users.models import User

from .models import CompetenceItem, ModeQuiz, QuizAnswer, QuizQuestion, QuizSession, ResultatDeclare
from .services import generer_session
from .views import _clean_quiz_markdown, _question_payload


def _make_question(lesson, numero, difficulte=Difficulte.MOYENNE, type_reponse=TypeReponse.OUVERTE, **kwargs):
    """Fixture catalog.Question - ne sert plus qu'à couvrir la lecture de l'historique
    pré-bascule (QuizQuestion.question), plus jamais peuplé par generer_session."""
    exercise = Exercise.objects.create(lesson=lesson, numero_exercice=numero, statut=StatutContenu.VALIDE)
    question = Question.objects.create(
        exercise=exercise, numero="1", ordre=1,
        enonce_markdown=f"Énoncé {numero}.", corrige_markdown=f"Corrigé {numero}.",
        difficulte_estimee=difficulte, type_reponse=type_reponse, **kwargs,
    )
    exercise.compile_from_questions()
    return question


def _make_competence_item(
    subject, cursus, theme=None, difficulte=Difficulte.MOYENNE, type_reponse=TypeReponse.OUVERTE, numero="1",
    **kwargs,
):
    """Fixture CompetenceItem - source réelle du Mode Quiz depuis la bascule. `statut`
    par défaut à VALIDE (le seul éligible en Quiz, voir _questions_eligibles) mais
    surchageable via kwargs pour tester le verrou de qualité lui-même."""
    theme = theme or Tag.objects.create(name=f"theme-{numero}")
    kwargs.setdefault("statut", StatutContenu.VALIDE)
    item = CompetenceItem.objects.create(
        theme=theme, subject=subject,
        enonce_markdown=f"Énoncé {numero}.", corrige_markdown=f"Corrigé {numero}.",
        difficulte_estimee=difficulte, type_reponse=type_reponse, **kwargs,
    )
    item.cursus.add(*(cursus if isinstance(cursus, (list, tuple)) else [cursus]))
    return item


class GenererSessionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677200001", password="x")
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.other_subject = Subject.objects.get(country__code="CM", code="FRANCAIS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.other_cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="D")

    def test_only_items_from_matching_cursus_are_eligible(self):
        _make_competence_item(self.subject, self.cursus, numero="1")
        _make_competence_item(self.subject, self.other_cursus, numero="2")

        session = generer_session(self.user, self.cursus, ModeQuiz.PRATIQUE, n=10)

        self.assertEqual(session.quiz_questions.count(), 1)

    def test_filters_by_subject(self):
        _make_competence_item(self.subject, self.cursus, numero="1")
        _make_competence_item(self.other_subject, self.cursus, numero="2")

        session = generer_session(self.user, self.cursus, ModeQuiz.PRATIQUE, subject=self.subject, n=10)

        self.assertEqual(session.quiz_questions.count(), 1)
        self.assertEqual(session.quiz_questions.first().competence_item.subject, self.subject)

    def test_filters_by_theme(self):
        theme = Tag.objects.create(name="dérivation")
        matching = _make_competence_item(self.subject, self.cursus, theme=theme, numero="1")
        _make_competence_item(self.subject, self.cursus, numero="2")  # thème différent

        session = generer_session(self.user, self.cursus, ModeQuiz.PRATIQUE, theme=theme, n=10)

        self.assertEqual(session.quiz_questions.count(), 1)
        self.assertEqual(session.quiz_questions.first().competence_item, matching)

    def test_brouillon_items_are_not_eligible(self):
        # Le verrou de qualité est désormais explicite (statut=VALIDE), pas une
        # heuristique de texte appliquée après coup - voir CompetenceItem.statut.
        _make_competence_item(self.subject, self.cursus, numero="1", statut=StatutContenu.BROUILLON)

        with self.assertRaises(ValueError):
            generer_session(self.user, self.cursus, ModeQuiz.PRATIQUE, n=10)

    def test_raises_when_no_item_eligible(self):
        with self.assertRaises(ValueError):
            generer_session(self.user, self.cursus, ModeQuiz.PRATIQUE, n=10)

    def test_diagnostic_mode_covers_a_range_of_difficulties(self):
        for i in range(5):
            _make_competence_item(self.subject, self.cursus, difficulte=Difficulte.FAIBLE, numero=f"faible-{i}")
        for i in range(5):
            _make_competence_item(self.subject, self.cursus, difficulte=Difficulte.MOYENNE, numero=f"moyenne-{i}")
        for i in range(5):
            _make_competence_item(self.subject, self.cursus, difficulte=Difficulte.ELEVEE, numero=f"elevee-{i}")

        session = generer_session(self.user, self.cursus, ModeQuiz.DIAGNOSTIC, n=10)

        difficultes = {qq.competence_item.difficulte_estimee for qq in session.quiz_questions.all()}
        self.assertEqual(session.quiz_questions.count(), 10)
        self.assertEqual(difficultes, {Difficulte.FAIBLE, Difficulte.MOYENNE, Difficulte.ELEVEE})


class QuizQuestionDeletionTests(TestCase):
    """QuizQuestion.question et QuizQuestion.competence_item doivent être CASCADE, pas
    PROTECT : la purge admin (voir catalog.admin.LessonAdmin.purge_view) supprime tout
    le contenu en bloc (Exercise -> Question en cascade) et ne doit jamais être bloquée
    parce qu'un item a été pioché dans un quiz - régression sur ce point précis, côté
    historique (question) comme côté source actuelle (competence_item)."""

    def test_deleting_exercise_cascades_through_quiz_question_without_protected_error(self):
        user = User.objects.create_user(phone_number="677200005", password="x")
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        lesson = Lesson.objects.create(
            title="Maths BAC C", subject=subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        lesson.cursus.add(cursus)
        question = _make_question(lesson, "1")
        exercise = question.exercise
        session = QuizSession.objects.create(user=user, cursus=cursus, mode=ModeQuiz.PRATIQUE)
        quiz_question = QuizQuestion.objects.create(session=session, question=question, ordre=1)

        exercise.delete()

        self.assertFalse(QuizQuestion.objects.filter(pk=quiz_question.pk).exists())

    def test_deleting_competence_item_cascades_through_quiz_question_without_protected_error(self):
        user = User.objects.create_user(phone_number="677200007", password="x")
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        item = _make_competence_item(subject, cursus, numero="1")
        session = QuizSession.objects.create(user=user, cursus=cursus, mode=ModeQuiz.PRATIQUE)
        quiz_question = QuizQuestion.objects.create(session=session, competence_item=item, ordre=1)

        item.delete()

        self.assertFalse(QuizQuestion.objects.filter(pk=quiz_question.pk).exists())


class QuizAnswerModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677200002", password="x")
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.qcm = _make_competence_item(
            subject, cursus, numero="1", type_reponse=TypeReponse.QCM,
            choix=[{"lettre": "a", "texte": "2x"}, {"lettre": "b", "texte": "x"}], reponse_correcte="a",
        )
        self.ouverte = _make_competence_item(subject, cursus, numero="2", type_reponse=TypeReponse.OUVERTE)
        session = QuizSession.objects.create(user=self.user, cursus=cursus, mode=ModeQuiz.PRATIQUE)
        self.qcm_qq = QuizQuestion.objects.create(session=session, competence_item=self.qcm, ordre=1)
        self.ouverte_qq = QuizQuestion.objects.create(session=session, competence_item=self.ouverte, ordre=2)

    def test_qcm_correct_choice_is_correcte(self):
        answer = QuizAnswer.objects.create(quiz_question=self.qcm_qq, reponse_choisie="a")
        self.assertTrue(answer.est_correcte)

    def test_qcm_wrong_choice_is_not_correcte(self):
        answer = QuizAnswer.objects.create(quiz_question=self.qcm_qq, reponse_choisie="b")
        self.assertFalse(answer.est_correcte)

    def test_open_question_reussi_is_correcte(self):
        answer = QuizAnswer.objects.create(quiz_question=self.ouverte_qq, resultat_declare=ResultatDeclare.REUSSI)
        self.assertTrue(answer.est_correcte)

    def test_open_question_echec_is_not_correcte(self):
        answer = QuizAnswer.objects.create(quiz_question=self.ouverte_qq, resultat_declare=ResultatDeclare.ECHEC)
        self.assertFalse(answer.est_correcte)


class CleanQuizMarkdownTests(TestCase):
    """Le cadre "épreuve papier" (en-tête Exercice/Problème, consigne de copie,
    barème) n'a jamais sa place dans le payload d'un item de quiz - toujours vrai pour
    un CompetenceItem (jamais rédigé avec ce cadre en premier lieu) et encore appliqué
    par _question_payload à la branche historique (catalog.Question), légitime tel
    quel dans la Lesson d'origine mais pas hors contexte. Cas réels rencontrés en
    production, avant la bascule."""

    def test_strips_heading_baked_into_first_question_enonce(self):
        text = "### Exercice 1 (5 points)\n\nRésoudre dans $\\mathbb R^2$ le système suivant : ..."
        self.assertEqual(
            _clean_quiz_markdown(text),
            "Résoudre dans $\\mathbb R^2$ le système suivant : ...",
        )

    def test_strips_probleme_heading(self):
        text = "### Problème (10 points)\n\nLe problème comporte deux parties indépendantes A et B."
        self.assertEqual(
            _clean_quiz_markdown(text),
            "Le problème comporte deux parties indépendantes A et B.",
        )

    def test_strips_exam_paper_instruction_and_bareme_from_intro(self):
        text = (
            "### Exercice 2 (5 points)\n\n"
            "Pour chacune des questions suivantes, 4 réponses vous sont proposées, mais une seule est juste ; "
            "écrivez-la sur votre feuille sans aucune autre justification. (Barème : 1,25 pt par réponse juste)"
        )
        cleaned = _clean_quiz_markdown(text)
        self.assertNotIn("Exercice", cleaned)
        self.assertNotIn("écrivez", cleaned)
        self.assertNotIn("Barème", cleaned)
        self.assertIn("Pour chacune des questions suivantes", cleaned)

    def test_leaves_text_without_exam_framing_untouched(self):
        text = "Calculer la dérivée de f."
        self.assertEqual(_clean_quiz_markdown(text), text)

    def test_handles_empty_string(self):
        self.assertEqual(_clean_quiz_markdown(""), "")


class LegacyQuestionPayloadTests(TestCase):
    """Couvre la branche historique de _question_payload (QuizQuestion.question) en
    isolation : plus jamais empruntée par generer_session depuis la bascule vers
    CompetenceItem, mais encore lue pour restituer les sessions déjà en base au moment
    de la bascule - une régression ici casserait silencieusement l'historique de quiz
    des élèves plutôt que les nouvelles sessions."""

    def test_legacy_question_payload_still_renders_lesson_link_and_numero(self):
        subject = Subject.objects.get(country__code="CM", code="MATHS")
        cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        lesson = Lesson.objects.create(
            title="Maths BAC C", subject=subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        lesson.cursus.add(cursus)
        question = _make_question(lesson, "1")
        user = User.objects.create_user(phone_number="677200006", password="x")
        session = QuizSession.objects.create(user=user, cursus=cursus, mode=ModeQuiz.PRATIQUE)
        quiz_question = QuizQuestion.objects.create(session=session, question=question, ordre=1)

        payload = _question_payload(quiz_question)

        self.assertEqual(payload["lesson_id"], lesson.id)
        self.assertEqual(payload["numero"], question.numero)
        self.assertEqual(payload["subject_label"], subject.label)


class QuizApiTests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.get(country__code="CM", code="MATHS")
        self.cursus = Cursus.objects.get(country__code="CM", examen=Examen.BAC, series__code="C")
        self.theme = Tag.objects.create(name="dérivation")
        self.item = _make_competence_item(self.subject, self.cursus, theme=self.theme, numero="1")

        self.user = User.objects.create_user(phone_number="677200003", password="x")
        self.client = APIClient()

    def _subscribe(self):
        Subscription.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
        )

    def test_start_session_requires_authentication(self):
        response = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        self.assertIn(response.status_code, (401, 403))

    def test_start_session_denied_without_subscription(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        self.assertEqual(response.status_code, 403)

    def test_start_session_rejects_cursus_from_an_inactive_country(self):
        # Un pays désactivé doit rester invisible même pour un cursus auquel
        # l'utilisateur serait déjà abonné - voir catalog.models.VisibleQuerySet et
        # le même principe appliqué ici à quiz.views.start_session.
        inactive = Country.objects.create(code="TG", label="Togo", actif=False)
        series = Series.objects.create(country=inactive, code="C", label="Maths")
        inactive_cursus = Cursus.objects.create(country=inactive, examen=Examen.BAC, series=series)
        Subscription.objects.create(
            user=self.user, cursus=inactive_cursus, expires_at=timezone.now() + timedelta(days=1),
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.post("/quiz/sessions/", {"cursus": inactive_cursus.id}, format="json")

        self.assertEqual(response.status_code, 404)

    def test_start_session_creates_session_with_questions(self):
        self._subscribe()
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/quiz/sessions/", {"cursus": self.cursus.id, "mode": ModeQuiz.PRATIQUE}, format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["total_questions"], 1)
        self.assertTrue(QuizSession.objects.filter(user=self.user, cursus=self.cursus).exists())

    def test_question_payload_exposes_theme_and_subject_without_exam_metadata(self):
        # Contrairement à l'ancien payload (source catalog.Question), un CompetenceItem
        # n'a ni lesson_id ni enonce_intro_markdown : il n'appartient à aucun Exercise,
        # donc rien de ce genre ne peut lui manquer une fois servi seul.
        self._subscribe()
        self.client.force_authenticate(user=self.user)

        response = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")

        payload = response.data["questions"][0]
        self.assertEqual(payload["theme"], self.theme.name)
        self.assertEqual(payload["subject_label"], self.subject.label)
        self.assertNotIn("lesson_id", payload)
        self.assertNotIn("enonce_intro_markdown", payload)

    def test_session_payload_exposes_cursus_display(self):
        self._subscribe()
        self.client.force_authenticate(user=self.user)

        response = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")

        self.assertEqual(response.data["cursus_display"], "BAC - Série C")

    def test_question_payload_never_leaks_answer_before_responding(self):
        self._subscribe()
        self.client.force_authenticate(user=self.user)
        start = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        quiz_question_id = start.data["questions"][0]["id"]

        detail = self.client.get(f"/quiz/sessions/{start.data['id']}/")

        payload = detail.data["questions"][0]
        self.assertNotIn("corrige_markdown", payload)
        self.assertNotIn("reponse_correcte", payload)
        self.assertNotIn("reponse", payload)
        self.assertEqual(payload["id"], quiz_question_id)

    def test_answering_reveals_corrige_and_computes_est_correcte(self):
        self._subscribe()
        self.client.force_authenticate(user=self.user)
        start = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        session_id = start.data["id"]
        quiz_question_id = start.data["questions"][0]["id"]

        response = self.client.post(
            f"/quiz/sessions/{session_id}/questions/{quiz_question_id}/answer/",
            {"resultat_declare": ResultatDeclare.REUSSI}, format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("corrige_markdown", response.data)
        self.assertTrue(response.data["reponse"]["est_correcte"])

        # Une fois répondu, la question révèle aussi le corrigé dans le détail de session.
        detail = self.client.get(f"/quiz/sessions/{session_id}/")
        self.assertIn("corrige_markdown", detail.data["questions"][0])

    def test_reveal_corrige_returns_content_without_recording_answer(self):
        self._subscribe()
        self.client.force_authenticate(user=self.user)
        start = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        session_id = start.data["id"]
        quiz_question_id = start.data["questions"][0]["id"]

        response = self.client.get(f"/quiz/sessions/{session_id}/questions/{quiz_question_id}/corrige/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["corrige_markdown"], self.item.corrige_markdown)
        self.assertFalse(QuizAnswer.objects.filter(quiz_question_id=quiz_question_id).exists())

        # Toujours pas répondu : le détail de session ne fuite pas encore le corrigé.
        detail = self.client.get(f"/quiz/sessions/{session_id}/")
        self.assertNotIn("corrige_markdown", detail.data["questions"][0])

    def test_reveal_corrige_denied_for_another_users_session(self):
        self._subscribe()
        self.client.force_authenticate(user=self.user)
        start = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        session_id = start.data["id"]
        quiz_question_id = start.data["questions"][0]["id"]

        other_user = User.objects.create_user(phone_number="677200004", password="x")
        self.client.force_authenticate(user=other_user)
        response = self.client.get(f"/quiz/sessions/{session_id}/questions/{quiz_question_id}/corrige/")

        self.assertEqual(response.status_code, 404)

    def test_complete_session_computes_score_by_theme(self):
        self._subscribe()
        self.client.force_authenticate(user=self.user)
        start = self.client.post("/quiz/sessions/", {"cursus": self.cursus.id}, format="json")
        session_id = start.data["id"]
        quiz_question_id = start.data["questions"][0]["id"]
        self.client.post(
            f"/quiz/sessions/{session_id}/questions/{quiz_question_id}/answer/",
            {"resultat_declare": ResultatDeclare.REUSSI}, format="json",
        )

        response = self.client.post(f"/quiz/sessions/{session_id}/completer/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["score"], 1)
        self.assertEqual(response.data["questions_repondues"], 1)
        self.assertEqual(response.data["par_theme"], [{"theme": "dérivation", "total": 1, "reussies": 1}])
        self.assertIsNotNone(QuizSession.objects.get(pk=session_id).completed_at)
