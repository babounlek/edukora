from datetime import timedelta

from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase

from access.models import NoteLibre
from catalog.models import Cursus, Examen, Exercise, Lesson, LessonType, Question, StatutContenu, Subject
from subscriptions.models import Subscription
from users.models import User

from . import extraction, services
from .models import Memo, StatutMemo


class _Base(APITestCase):
    def setUp(self):
        maths = Subject.objects.get(code="MATHS")
        self.cursus = Cursus.objects.filter(examen=Examen.BEPC, country=maths.country).first()
        self.subject = Subject.objects.create(country=maths.country, code="ECM_TEST", label="Éducation Civique")
        self.user = User.objects.create_user(phone_number="677600001", password="x")
        self.profil = self.user.profils.first()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def memo(self, terme="Scrutin", **extra):
        champs = {
            "definition": "Ensemble des opérations par lesquelles les électeurs désignent leurs représentants.",
            "statut": StatutMemo.PUBLIE, "relu_par_enseignant": True,
            "sessions": [{"annee": 2019, "origine": "OFFICIEL"}],
        }
        champs.update(extra)
        m = Memo.objects.create(subject=self.subject, terme=terme, **champs)
        m.cursus.add(self.cursus)
        return m

    def abonner(self):
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=30),
        )


@override_settings(MEMOS_MONTRER_BROUILLONS=False)
class LectureTests(_Base):
    def test_a_draft_or_an_unreviewed_card_is_never_shown(self):
        self.memo("Publiée")
        self.memo("Brouillon", statut=StatutMemo.BROUILLON)
        # Publiée sans relecture : le modèle la remet en brouillon.
        non_relue = self.memo("Non relue", relu_par_enseignant=False)
        self.assertEqual(non_relue.statut, StatutMemo.BROUILLON)
        data = self.client.get(f"/memos/fiches/?cursus={self.cursus.pk}&matiere={self.subject.pk}").data
        self.assertEqual([f["terme"] for f in data["fiches"]], ["Publiée"])

    def test_without_a_subscription_only_free_cards_give_their_definition(self):
        self.memo("Gratuite", gratuit=True)
        self.memo("Payante")
        data = self.client.get(f"/memos/fiches/?cursus={self.cursus.pk}&matiere={self.subject.pk}").data
        par_terme = {f["terme"]: f for f in data["fiches"]}
        self.assertFalse(data["abonne"])
        self.assertIsNotNone(par_terme["Gratuite"]["definition"])
        self.assertIsNone(par_terme["Payante"]["definition"])
        self.assertTrue(par_terme["Payante"]["verrouillee"])
        # Le terme et les sessions restent visibles : c'est ce qui donne envie.
        self.assertEqual(par_terme["Payante"]["sessions"], [{"annee": 2019, "origine": "OFFICIEL"}])

    def test_a_subscriber_reads_everything_and_a_visitor_reads_the_free_ones(self):
        self.memo("Gratuite", gratuit=True)
        self.memo("Payante")
        visiteur = APIClient().get(f"/memos/fiches/?cursus={self.cursus.pk}&matiere={self.subject.pk}").data
        self.assertEqual(sum(1 for f in visiteur["fiches"] if f["definition"]), 1)
        self.abonner()
        abonne = self.client.get(f"/memos/fiches/?cursus={self.cursus.pk}&matiere={self.subject.pk}").data
        self.assertTrue(abonne["abonne"])
        self.assertTrue(all(f["definition"] for f in abonne["fiches"]))

    def test_the_subjects_list_counts_cards_per_subject(self):
        self.memo("A", gratuit=True)
        self.memo("B")
        data = self.client.get(f"/memos/matieres/?cursus={self.cursus.pk}").data
        self.assertEqual(data["matieres"], [{
            "matiere_id": self.subject.pk, "matiere": "Éducation Civique", "matiere_code": "ECM_TEST",
            "total": 2, "gratuites": 1,
        }])
        self.assertEqual(self.client.get("/memos/matieres/").status_code, 400)


@override_settings(MEMOS_MONTRER_BROUILLONS=False)
class GarderTests(_Base):
    def test_keeping_a_card_makes_a_review_note_once(self):
        memo = self.memo(gratuit=True, exemple="Exemple : l'élection présidentielle.")
        r = self.client.post(f"/memos/fiches/{memo.pk}/garder/")
        self.assertEqual(r.status_code, 201)
        note = NoteLibre.objects.get()
        # Le terme est le recto de la carte de révision, la définition son verso.
        self.assertEqual((note.citation, note.origine, note.subject_id), ("Scrutin", "fiche", self.subject.pk))
        self.assertIn("Exemple", note.note)
        self.assertEqual(self.client.post(f"/memos/fiches/{memo.pk}/garder/").status_code, 200)
        self.assertEqual(NoteLibre.objects.count(), 1)
        data = self.client.get(f"/memos/fiches/?cursus={self.cursus.pk}&matiere={self.subject.pk}").data
        self.assertTrue(data["fiches"][0]["gardee"])

    def test_a_locked_card_cannot_be_kept_and_a_visitor_cannot_keep(self):
        memo = self.memo()
        self.assertEqual(self.client.post(f"/memos/fiches/{memo.pk}/garder/").status_code, 403)
        self.assertEqual(APIClient().post(f"/memos/fiches/{memo.pk}/garder/").status_code, 401)
        self.abonner()
        self.assertEqual(self.client.post(f"/memos/fiches/{memo.pk}/garder/").status_code, 201)


class ExtractionTests(_Base):
    def _question(self, annee, corrige, enonce="Définis : scrutin, tontine.", origine="OFFICIEL"):
        lesson = Lesson.objects.create(
            title=f"ECM {annee} {origine}", subject=self.subject, year=annee, origine=origine,
            lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        lesson.cursus.add(self.cursus)
        exercice = Exercise.objects.create(lesson=lesson, numero_exercice="1")
        return Question.objects.create(exercise=exercice, numero="1", ordre=1, enonce_markdown=enonce, corrige_markdown=corrige)

    def test_definitions_are_read_from_the_solutions_and_grouped_by_term(self):
        self._question(2018, "### Rappel de méthode\nCourt.\n\n**Scrutin** : ancienne rédaction de la définition du scrutin.")
        self._question(
            2019,
            "**Astuce** : ne pas confondre avec autre chose du tout.\n"
            "**Le scrutin** : ensemble des opérations par lesquelles les électeurs votent\n"
            "- **Tontine** : association d'entraide financière entre ses membres.",
        )
        self._question(2020, "**Hors sujet** : cette ligne n'est pas une définition demandée.", enonce="Cite deux symboles.")
        relevees = extraction.relever(self.subject)
        self.assertEqual([n["terme"] for n in relevees], ["Scrutin", "Tontine"])
        scrutin = relevees[0]
        self.assertEqual([s["annee"] for s in scrutin["sessions"]], [2018, 2019])
        # La rédaction la plus récente, terminée par un point.
        self.assertEqual(scrutin["definition"], "Ensemble des opérations par lesquelles les électeurs votent.")

    def test_generated_cards_are_drafts_and_manual_edits_are_kept(self):
        self._question(2019, "**Scrutin** : ensemble des opérations par lesquelles les électeurs votent.")
        bilan = extraction.enregistrer(self.subject, extraction.relever(self.subject))
        self.assertEqual(bilan["creees"], 1)
        memo = Memo.objects.get()
        self.assertEqual((memo.statut, memo.relu_par_enseignant, memo.gratuit), (StatutMemo.BROUILLON, False, True))
        self.assertEqual(list(memo.cursus.all()), [self.cursus])
        memo.definition = "Texte corrigé par l'enseignant."
        memo.modifie_a_la_main = True
        memo.save()
        bilan = extraction.enregistrer(self.subject, extraction.relever(self.subject))
        self.assertEqual(bilan["laissees"], 1)
        memo.refresh_from_db()
        self.assertEqual(memo.definition, "Texte corrigé par l'enseignant.")

    @override_settings(MEMOS_MONTRER_BROUILLONS=True)
    def test_in_development_drafts_show_flagged_as_to_review(self):
        m = Memo.objects.create(subject=self.subject, terme="Brouillon", definition="Une définition encore à relire par un enseignant.", gratuit=True)
        m.cursus.add(self.cursus)
        data = self.client.get(f"/memos/fiches/?cursus={self.cursus.pk}&matiere={self.subject.pk}").data
        self.assertTrue(data["fiches"][0]["a_relire"])
        self.assertEqual(services.visibles().count(), 1)
