"""
Couvre le risque principal du module : le contrôle d'accès au contenu payant. Deux
familles de vérité à ne jamais laisser diverger - has_access() (la règle) et les vues
read_*/preview_* (son application, y compris ce que preview_* n'expose jamais, à savoir
le corrigé/les sections payantes) - donc testées séparément ici.
"""

from datetime import timedelta

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Cours, Cursus, Examen, Exercise, Lesson, LessonType, StatutContenu, Subject
from inedit.models import Blueprint, EpreuveInedite
from subscriptions.models import InscriptionInedite, Subscription
from users.models import User

from .models import LectureProgress
from .services import has_access, has_access_inedite


class HasAccessTests(TestCase):
    """La règle elle-même, indépendamment de toute vue."""

    def setUp(self):
        self.user = User.objects.create_user(phone_number="677100001", password="x")
        self.subject = Subject.objects.get(code="MATHS")
        self.cursus_c = Cursus.objects.get(examen=Examen.BAC, series__code="C")
        self.cursus_d = Cursus.objects.get(examen=Examen.BAC, series__code="D")
        self.lesson = Lesson.objects.create(
            title="Maths BAC C", subject=self.subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        self.lesson.cursus.add(self.cursus_c)

    def test_no_subscription_denies_access(self):
        self.assertFalse(has_access(self.user, self.lesson))

    def test_active_subscription_matching_cursus_grants_access(self):
        Subscription.objects.create(
            user=self.user, cursus=self.cursus_c, expires_at=timezone.now() + timedelta(days=1),
        )
        self.assertTrue(has_access(self.user, self.lesson))

    def test_expired_subscription_denies_access(self):
        Subscription.objects.create(
            user=self.user, cursus=self.cursus_c, expires_at=timezone.now() - timedelta(days=1),
        )
        self.assertFalse(has_access(self.user, self.lesson))

    def test_subscription_to_different_cursus_denies_access(self):
        """Un abonnement Série D ne doit jamais donner accès à du contenu Série C."""
        Subscription.objects.create(
            user=self.user, cursus=self.cursus_d, expires_at=timezone.now() + timedelta(days=1),
        )
        self.assertFalse(has_access(self.user, self.lesson))

    def test_lesson_common_to_multiple_series_grants_access_via_any_matching_subscription(self):
        """Épreuve commune C/E (ou ici C/D) : un abonnement sur l'une des deux séries suffit."""
        self.lesson.cursus.add(self.cursus_d)
        Subscription.objects.create(
            user=self.user, cursus=self.cursus_d, expires_at=timezone.now() + timedelta(days=1),
        )
        self.assertTrue(has_access(self.user, self.lesson))

    def test_cours_toutes_series_grants_access_with_any_active_subscription(self):
        cours = Cours.objects.create(titre="Notion commune", subject=self.subject, statut=StatutContenu.VALIDE)
        Subscription.objects.create(
            user=self.user, cursus=self.cursus_d, expires_at=timezone.now() + timedelta(days=1),
        )
        self.assertTrue(has_access(self.user, cours))

    def test_cours_toutes_series_denies_access_without_any_subscription(self):
        cours = Cours.objects.create(titre="Notion commune", subject=self.subject, statut=StatutContenu.VALIDE)
        self.assertFalse(has_access(self.user, cours))


class HasAccessInediteTests(TestCase):
    """
    has_access_inedite - même risque que HasAccessTests, mais côté add-on (voir
    subscriptions.InscriptionInedite) : gate EpreuveInedite.cursus (M2M, comme
    Lesson.cursus - une épreuve inédite peut être commune à plusieurs séries, ex. Maths
    BAC C/E), jamais Subscription, jamais de court-circuit vitrine (décision "corrigé
    gaté comme le reste", audit "Épreuves Inédites").
    """

    def setUp(self):
        self.user = User.objects.create_user(phone_number="677100010", password="x")
        self.subject = Subject.objects.get(code="MATHS")
        self.cursus_c = Cursus.objects.get(examen=Examen.BAC, series__code="C")
        self.cursus_d = Cursus.objects.get(examen=Examen.BAC, series__code="D")
        blueprint = Blueprint.objects.create(subject=self.subject, titre="Blueprint test")
        blueprint.cursus.set([self.cursus_c])
        self.epreuve = EpreuveInedite.objects.create(blueprint=blueprint, subject=self.subject, titre="Épreuve test")
        self.epreuve.cursus.set([self.cursus_c])

    def test_anonymous_is_denied(self):
        self.assertFalse(has_access_inedite(AnonymousUser(), self.epreuve))

    def test_no_inscription_denies_access(self):
        self.assertFalse(has_access_inedite(self.user, self.epreuve))

    def test_active_inscription_matching_cursus_grants_access(self):
        InscriptionInedite.objects.create(
            user=self.user, cursus=self.cursus_c, expires_at=timezone.now() + timedelta(days=1),
        )
        self.assertTrue(has_access_inedite(self.user, self.epreuve))

    def test_expired_inscription_denies_access(self):
        InscriptionInedite.objects.create(
            user=self.user, cursus=self.cursus_c, expires_at=timezone.now() - timedelta(days=1),
        )
        self.assertFalse(has_access_inedite(self.user, self.epreuve))

    def test_inscription_to_a_different_cursus_denies_access(self):
        InscriptionInedite.objects.create(
            user=self.user, cursus=self.cursus_d, expires_at=timezone.now() + timedelta(days=1),
        )
        self.assertFalse(has_access_inedite(self.user, self.epreuve))

    def test_base_subscription_alone_never_grants_inedit_access(self):
        """Indépendance des deux accès (décision "C2") - un abonnement de base ne doit
        jamais suffire pour l'add-on, et réciproquement (voir HasAccessTests)."""
        Subscription.objects.create(
            user=self.user, cursus=self.cursus_c, expires_at=timezone.now() + timedelta(days=1),
        )
        self.assertFalse(has_access_inedite(self.user, self.epreuve))

    def test_epreuve_common_to_multiple_series_grants_access_via_any_matching_inscription(self):
        """Épreuve commune C/D (ex. Maths BAC C/E en pratique) : une inscription sur
        l'une des deux séries suffit - reproduit le bug rapporté (une épreuve inédite
        Maths BAC C/E doit débloquer pour un abonné de C seul comme de E seul)."""
        self.epreuve.cursus.add(self.cursus_d)
        InscriptionInedite.objects.create(
            user=self.user, cursus=self.cursus_d, expires_at=timezone.now() + timedelta(days=1),
        )
        self.assertTrue(has_access_inedite(self.user, self.epreuve))


class ReadLessonAPITests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.get(code="MATHS")
        self.cursus = Cursus.objects.get(examen=Examen.BAC, series__code="C")
        self.other_cursus = Cursus.objects.get(examen=Examen.BAC, series__code="D")
        self.lesson = Lesson.objects.create(
            title="Maths BAC C 2024", subject=self.subject, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE, content_markdown="## Corrigé secret",
        )
        self.lesson.cursus.add(self.cursus)
        self.user = User.objects.create_user(phone_number="677100002", password="x")
        self.client = APIClient()

    def test_read_requires_authentication(self):
        response = self.client.get(f"/access/read/{self.lesson.id}/")
        self.assertIn(response.status_code, (401, 403))

    def test_read_denied_without_subscription(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/access/read/{self.lesson.id}/")
        self.assertEqual(response.status_code, 403)
        self.assertNotIn("Corrigé secret", str(response.data))

    def test_read_denied_with_wrong_cursus_subscription(self):
        Subscription.objects.create(
            user=self.user, cursus=self.other_cursus, expires_at=timezone.now() + timedelta(days=1),
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/access/read/{self.lesson.id}/")
        self.assertEqual(response.status_code, 403)

    def test_read_allowed_with_matching_subscription_and_tracks_progress(self):
        Subscription.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f"/access/read/{self.lesson.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["content_markdown"], "## Corrigé secret")
        # Distingue le format de lecture côté frontend (article long-format vs. fiche
        # courte recto/verso, voir EpreuveReaderPage.tsx) - absent de header_info(),
        # qui ne porte que des métadonnées d'affichage.
        self.assertEqual(response.data["lesson_type"], LessonType.CORR)
        self.assertTrue(LectureProgress.objects.filter(user=self.user, lesson=self.lesson).exists())

    def test_reading_twice_does_not_duplicate_progress(self):
        Subscription.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
        )
        self.client.force_authenticate(user=self.user)

        self.client.get(f"/access/read/{self.lesson.id}/")
        self.client.get(f"/access/read/{self.lesson.id}/")

        self.assertEqual(LectureProgress.objects.filter(user=self.user, lesson=self.lesson).count(), 1)

    def test_read_exposes_an_empty_exercises_breakdown_for_a_lesson_without_exercise_rows(self):
        # Ce Lesson n'a que content_markdown, aucun Exercise (voir setUp) - le
        # frontend doit alors retomber dessus plutôt que sur une liste vide qu'il
        # afficherait à tort comme "pas de contenu" (voir EpreuveReaderPage.tsx).
        Subscription.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f"/access/read/{self.lesson.id}/")

        self.assertEqual(response.data["exercises"], [])

    def test_read_exposes_enonce_and_corrige_separately_per_exercise(self):
        # Reco d'audit UX : l'énoncé doit pouvoir être replié indépendamment du
        # corrigé côté lecture - voir Lesson.exercises_breakdown.
        Exercise.objects.create(
            lesson=self.lesson, numero_exercice="1",
            enonce_markdown="Énoncé exercice 1", corrige_markdown="### Corrigé\n\nCorrigé exercice 1",
            statut=StatutContenu.VALIDE,
        )
        Subscription.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f"/access/read/{self.lesson.id}/")

        self.assertEqual(len(response.data["exercises"]), 1)
        self.assertEqual(response.data["exercises"][0]["numero_exercice"], "1")
        self.assertEqual(response.data["exercises"][0]["enonce_markdown"], "Énoncé exercice 1")
        self.assertIn("Corrigé exercice 1", response.data["exercises"][0]["corrige_markdown"])

    def test_read_exposes_the_exercise_intro_separately_from_the_toggleable_enonce(self):
        # La référence de l'exercice/le préambule partagé doivent rester visibles même
        # quand l'élève lit le corrigé sans déplier l'énoncé complet (voir
        # EpreuveReaderPage.tsx, qui affiche ce champ hors du EnonceToggle) - voir
        # Lesson.exercises_breakdown.
        Exercise.objects.create(
            lesson=self.lesson, numero_exercice="1",
            enonce_intro_markdown="**Exercice 1 (6 points)**\n\nDonnées communes.",
            enonce_markdown="**Exercice 1 (6 points)**\n\nDonnées communes.\n\nQuestion posée.",
            corrige_markdown="### Corrigé\n\nCorrigé exercice 1",
            statut=StatutContenu.VALIDE,
        )
        Subscription.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f"/access/read/{self.lesson.id}/")

        exercise_data = response.data["exercises"][0]
        self.assertEqual(exercise_data["enonce_intro_markdown"], "**Exercice 1 (6 points)**\n\nDonnées communes.")
        self.assertEqual(exercise_data["enonce_markdown"], "Question posée.")


class PreviewLessonAPITests(TestCase):
    """Le point d'entrée public : jamais authentifié, jamais le corrigé."""

    def setUp(self):
        self.subject = Subject.objects.get(code="MATHS")
        self.cursus = Cursus.objects.get(examen=Examen.BAC, series__code="C")
        self.lesson = Lesson.objects.create(
            title="Maths BAC C 2024", subject=self.subject, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE, content_markdown="## Corrigé secret ne doit jamais sortir ici",
        )
        Exercise.objects.create(
            lesson=self.lesson, numero_exercice="1",
            enonce_markdown="Énoncé public", corrige_markdown="Corrigé confidentiel",
            statut=StatutContenu.VALIDE,
        )
        self.lesson.cursus.add(self.cursus)
        self.client = APIClient()

    def test_preview_accessible_without_authentication(self):
        response = self.client.get(f"/access/preview/{self.lesson.id}/")
        self.assertEqual(response.status_code, 200)

    def test_preview_never_exposes_corrige(self):
        response = self.client.get(f"/access/preview/{self.lesson.id}/")
        self.assertNotIn("content_markdown", response.data)
        self.assertNotIn("Corrigé confidentiel", str(response.data))
        self.assertIn("Énoncé public", response.data["preview_markdown"])

    def test_preview_exposes_the_sujet_split_per_exercise(self):
        # Sert les liens "Lire le corrigé de cet exercice" de la fiche, qui pointent
        # vers /lire#exercice-{numero} - voir EpreuveDetailPage.
        response = self.client.get(f"/access/preview/{self.lesson.id}/")

        self.assertEqual(len(response.data["exercises"]), 1)
        exercise_data = response.data["exercises"][0]
        self.assertEqual(exercise_data["numero_exercice"], "1")
        self.assertIn("Énoncé public", exercise_data["enonce_markdown"])
        self.assertNotIn("corrige_markdown", exercise_data)


class ReadCoursAPITests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.get(code="MATHS")
        self.cursus = Cursus.objects.get(examen=Examen.BAC, series__code="C")
        self.cours = Cours.objects.create(
            titre="Résolution d'équations", subject=self.subject, statut=StatutContenu.VALIDE,
            sections_raw=[
                {"type": "accroche", "contenu_markdown": "Accroche publique"},
                {"type": "exemple_resolu", "enonce_markdown": "Exemple payant"},
            ],
        )
        self.cours.compile_from_sections()
        self.cours.cursus.add(self.cursus)
        self.user = User.objects.create_user(phone_number="677100003", password="x")
        self.client = APIClient()

    def test_read_cours_denied_without_subscription(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/access/cours/read/{self.cours.id}/")
        self.assertEqual(response.status_code, 403)

    def test_read_cours_allowed_with_subscription_and_tracks_progress(self):
        Subscription.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f"/access/cours/read/{self.cours.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Exemple payant", response.data["content_markdown"])
        self.assertTrue(LectureProgress.objects.filter(user=self.user, cours=self.cours).exists())

    def test_preview_cours_never_exposes_paid_sections(self):
        response = self.client.get(f"/access/cours/preview/{self.cours.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Accroche publique", response.data["preview_markdown"])
        self.assertNotIn("Exemple payant", response.data["preview_markdown"])

    def test_read_cours_accepts_slug_as_well_as_numeric_id(self):
        # URL publique désormais /cours/<slug>/lire (voir l'audit UX) - l'id numérique
        # reste accepté en compat historique (voir Cours.save/par_slug_ou_id).
        Subscription.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f"/access/cours/read/{self.cours.slug}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], self.cours.titre)

    def test_preview_cours_accepts_slug_as_well_as_numeric_id(self):
        response = self.client.get(f"/access/cours/preview/{self.cours.slug}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Accroche publique", response.data["preview_markdown"])


class MyProgressionAPITests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.get(code="MATHS")
        self.cursus = Cursus.objects.get(examen=Examen.BAC, series__code="C")
        self.lesson = Lesson.objects.create(
            title="Maths BAC C 2024", subject=self.subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        self.lesson.cursus.add(self.cursus)
        self.user = User.objects.create_user(phone_number="677100004", password="x")
        Subscription.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_progression_lists_only_own_read_lessons(self):
        self.client.get(f"/access/read/{self.lesson.id}/")

        response = self.client.get("/access/progression/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["lessons"]), 1)
        self.assertEqual(response.data["lessons"][0]["id"], self.lesson.id)

    def test_progression_empty_before_reading_anything(self):
        response = self.client.get("/access/progression/")
        self.assertEqual(response.data["lessons"], [])
        self.assertEqual(response.data["cours"], [])
