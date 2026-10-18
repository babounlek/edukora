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

from catalog.models import Cours, Cursus, Examen, Exercise, Lesson, LessonType, RappelDeMethode, StatutContenu, Subject
from inedit.models import Blueprint, EpreuveInedite
from subscriptions.models import DureeMode, InscriptionInedite, Subscription
from rest_framework_simplejwt.tokens import AccessToken

from users.models import Profil, User

from .models import LectureProgress
from .services import (
    bulk_active_inedite_cursus_ids,
    bulk_active_subscription_cursus_ids,
    has_access,
    has_access_inedite,
    a_acces_exercices_cours,
    has_access_jusqua_examen,
)


class HasAccessTests(TestCase):
    """La règle elle-même, indépendamment de toute vue."""

    def setUp(self):
        self.user = User.objects.create_user(phone_number="677100001", password="x")
        self.profil = self.user.profils.first()
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
            user=self.user, profil=self.profil, cursus=self.cursus_c, expires_at=timezone.now() + timedelta(days=1),
        )
        self.assertTrue(has_access(self.user, self.lesson))

    def test_expired_subscription_denies_access(self):
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus_c, expires_at=timezone.now() - timedelta(days=1),
        )
        self.assertFalse(has_access(self.user, self.lesson))

    def test_subscription_to_different_cursus_denies_access(self):
        """Un abonnement Série D ne doit jamais donner accès à du contenu Série C."""
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus_d, expires_at=timezone.now() + timedelta(days=1),
        )
        self.assertFalse(has_access(self.user, self.lesson))

    def test_lesson_common_to_multiple_series_grants_access_via_any_matching_subscription(self):
        """Épreuve commune C/E (ou ici C/D) : un abonnement sur l'une des deux séries suffit."""
        self.lesson.cursus.add(self.cursus_d)
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus_d, expires_at=timezone.now() + timedelta(days=1),
        )
        self.assertTrue(has_access(self.user, self.lesson))

    def test_un_cours_est_lisible_par_tous_meme_sans_abonnement(self):
        # Décision du 2026-10-14 : tout cours est libre en lecture, y compris pour un visiteur anonyme.
        cours = Cours.objects.create(titre="Notion commune", subject=self.subject, statut=StatutContenu.VALIDE)
        self.assertTrue(has_access(self.user, cours))
        self.assertTrue(has_access(AnonymousUser(), cours))

    def test_cours_toutes_series_ouvre_ses_exercices_avec_n_importe_quel_abonnement_actif(self):
        cours = Cours.objects.create(titre="Notion commune", subject=self.subject, statut=StatutContenu.VALIDE)
        self.assertFalse(a_acces_exercices_cours(self.user, cours))
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus_d, expires_at=timezone.now() + timedelta(days=1),
        )
        self.assertTrue(a_acces_exercices_cours(self.user, cours))

    def test_cours_cite_par_une_epreuve_gratuite_ne_libere_pas_ses_exercices(self):
        # Cours.est_vitrine (property) reste dérivée des rappels de méthode source ; elle n'ouvre plus que la
        # lecture - déjà libre pour tous - jamais les exercices d'application.
        vitrine_lesson = Lesson.objects.create(
            title="Maths BEPC vitrine", subject=self.subject, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE, est_vitrine=True,
        )
        exercise = Exercise.objects.create(lesson=vitrine_lesson, numero_exercice="1", statut=StatutContenu.VALIDE)
        cours = Cours.objects.create(titre="Notion vitrine", subject=self.subject, statut=StatutContenu.VALIDE)
        RappelDeMethode.objects.create(
            exercise=exercise, external_id="rdm-vitrine-test", competence="Test",
            contenu_markdown="Contenu.", cours=cours,
        )

        self.assertTrue(cours.est_vitrine)
        self.assertTrue(has_access(AnonymousUser(), cours))
        self.assertFalse(a_acces_exercices_cours(AnonymousUser(), cours))


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
        self.profil = self.user.profils.first()
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
            user=self.user, profil=self.profil, cursus=self.cursus_c, expires_at=timezone.now() + timedelta(days=1),
        )
        self.assertTrue(has_access_inedite(self.user, self.epreuve))

    def test_expired_inscription_denies_access(self):
        InscriptionInedite.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus_c, expires_at=timezone.now() - timedelta(days=1),
        )
        self.assertFalse(has_access_inedite(self.user, self.epreuve))

    def test_inscription_to_a_different_cursus_denies_access(self):
        InscriptionInedite.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus_d, expires_at=timezone.now() + timedelta(days=1),
        )
        self.assertFalse(has_access_inedite(self.user, self.epreuve))

    def test_base_subscription_alone_never_grants_inedit_access(self):
        """Indépendance des deux accès (décision "C2") - un abonnement de base ne doit
        jamais suffire pour l'add-on, et réciproquement (voir HasAccessTests)."""
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus_c, expires_at=timezone.now() + timedelta(days=1),
        )
        self.assertFalse(has_access_inedite(self.user, self.epreuve))

    def test_epreuve_common_to_multiple_series_grants_access_via_any_matching_inscription(self):
        """Épreuve commune C/D (ex. Maths BAC C/E en pratique) : une inscription sur
        l'une des deux séries suffit - reproduit le bug rapporté (une épreuve inédite
        Maths BAC C/E doit débloquer pour un abonné de C seul comme de E seul)."""
        self.epreuve.cursus.add(self.cursus_d)
        InscriptionInedite.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus_d, expires_at=timezone.now() + timedelta(days=1),
        )
        self.assertTrue(has_access_inedite(self.user, self.epreuve))


class HasAccessJusquaExamenTests(TestCase):
    """
    has_access_jusqua_examen - distinct de has_access, qui accepte n'importe quel palier
    (Mensuel comme Jusqu'à l'Examen) pour le contenu de base. Prend directement un Cursus
    (comme has_access_fiches), pas un objet exposant `.cursus` : pensé pour gater des
    fonctionnalités transverses au cursus (ex. ThemesFrequentsView), pas un contenu
    précis.
    """

    def setUp(self):
        self.user = User.objects.create_user(phone_number="677100020", password="x")
        self.profil = self.user.profils.first()
        self.cursus_c = Cursus.objects.get(examen=Examen.BAC, series__code="C")
        self.cursus_d = Cursus.objects.get(examen=Examen.BAC, series__code="D")

    def test_anonymous_is_denied(self):
        self.assertFalse(has_access_jusqua_examen(AnonymousUser(), self.cursus_c))

    def test_no_subscription_denies_access(self):
        self.assertFalse(has_access_jusqua_examen(self.user, self.cursus_c))

    def test_fixe_subscription_denies_access(self):
        """Un abonnement Mensuel actif ne donne PAS accès - c'est tout l'objet de ce
        garde, par opposition à has_access qui l'aurait accordé."""
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus_c, expires_at=timezone.now() + timedelta(days=1),
            duration_mode=DureeMode.FIXE,
        )
        self.assertFalse(has_access_jusqua_examen(self.user, self.cursus_c))

    def test_jusqua_examen_subscription_grants_access(self):
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus_c, expires_at=timezone.now() + timedelta(days=1),
            duration_mode=DureeMode.JUSQUA_EXAMEN,
        )
        self.assertTrue(has_access_jusqua_examen(self.user, self.cursus_c))

    def test_expired_jusqua_examen_subscription_denies_access(self):
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus_c, expires_at=timezone.now() - timedelta(days=1),
            duration_mode=DureeMode.JUSQUA_EXAMEN,
        )
        self.assertFalse(has_access_jusqua_examen(self.user, self.cursus_c))

    def test_jusqua_examen_subscription_on_a_different_cursus_denies_access(self):
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus_d, expires_at=timezone.now() + timedelta(days=1),
            duration_mode=DureeMode.JUSQUA_EXAMEN,
        )
        self.assertFalse(has_access_jusqua_examen(self.user, self.cursus_c))


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
        self.profil = self.user.profils.first()
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
            user=self.user, profil=self.profil, cursus=self.other_cursus, expires_at=timezone.now() + timedelta(days=1),
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/access/read/{self.lesson.id}/")
        self.assertEqual(response.status_code, 403)

    def test_read_allowed_with_matching_subscription_and_tracks_progress(self):
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f"/access/read/{self.lesson.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["content_markdown"], "## Corrigé secret")
        # Distingue le format de lecture côté frontend (article long-format vs. fiche
        # courte recto/verso, voir EpreuveReaderPage.tsx) - absent de header_info(),
        # qui ne porte que des métadonnées d'affichage.
        self.assertEqual(response.data["lesson_type"], LessonType.CORR)
        self.assertTrue(LectureProgress.objects.filter(profil=self.profil, lesson=self.lesson).exists())

    def test_reading_twice_does_not_duplicate_progress(self):
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
        )
        self.client.force_authenticate(user=self.user)

        self.client.get(f"/access/read/{self.lesson.id}/")
        self.client.get(f"/access/read/{self.lesson.id}/")

        self.assertEqual(LectureProgress.objects.filter(profil=self.profil, lesson=self.lesson).count(), 1)

    def test_read_exposes_an_empty_exercises_breakdown_for_a_lesson_without_exercise_rows(self):
        # Ce Lesson n'a que content_markdown, aucun Exercise (voir setUp) - le
        # frontend doit alors retomber dessus plutôt que sur une liste vide qu'il
        # afficherait à tort comme "pas de contenu" (voir EpreuveReaderPage.tsx).
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
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
            user=self.user, profil=self.profil, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
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
        # Lesson.exercises_breakdown. Le repère "Exercice 1 (6 points)" lui-même est un
        # repère nu (numéro + barème entre parenthèses, sans sous-titre réel) et
        # disparaît de l'intro pour cette Lesson à exercice unique - voir
        # rendering._strip_solo_exercise_heading, testé indépendamment dans
        # catalog.tests.LessonExercisesBreakdownTests.test_solo_exercise_heading_is_stripped_from_intro.
        Exercise.objects.create(
            lesson=self.lesson, numero_exercice="1",
            enonce_intro_markdown="**Exercice 1 (6 points)**\n\nDonnées communes.",
            enonce_markdown="**Exercice 1 (6 points)**\n\nDonnées communes.\n\nQuestion posée.",
            corrige_markdown="### Corrigé\n\nCorrigé exercice 1",
            statut=StatutContenu.VALIDE,
        )
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f"/access/read/{self.lesson.id}/")

        exercise_data = response.data["exercises"][0]
        self.assertEqual(exercise_data["enonce_intro_markdown"], "Données communes.")
        self.assertEqual(exercise_data["enonce_markdown"], "Question posée.")

    def test_read_exposes_the_epreuve_wide_introduction_separately_from_the_exercises(self):
        # Distinct de enonce_intro_markdown (propre à UN exercice, voir le test
        # ci-dessus) : une consigne d'épreuve entière ne doit apparaître qu'une seule
        # fois, jamais nichée dans un exercice en particulier - voir
        # Lesson.introduction_markdown et EpreuveReaderPage.tsx.
        self.lesson.introduction_markdown = "Le candidat traitera au choix l'un des trois sujets proposés."
        self.lesson.save(update_fields=["introduction_markdown"])
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f"/access/read/{self.lesson.id}/")

        self.assertEqual(
            response.data["introduction_markdown"],
            "Le candidat traitera au choix l'un des trois sujets proposés.",
        )

    def test_read_exposes_the_structured_choice_rules(self):
        regles = [{"type": "parmi", "portee": "SECTION A", "repondre": 2, "sur": 3}]
        self.lesson.regles_choix = regles
        self.lesson.save(update_fields=["regles_choix"])
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
        )
        self.client.force_authenticate(user=self.user)

        self.assertEqual(self.client.get(f"/access/read/{self.lesson.id}/").data["regles_choix"], regles)


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

    def test_preview_exposes_the_epreuve_wide_introduction(self):
        self.lesson.introduction_markdown = "L'épreuve comporte deux parties indépendantes."
        self.lesson.save(update_fields=["introduction_markdown"])

        response = self.client.get(f"/access/preview/{self.lesson.id}/")

        self.assertEqual(response.data["introduction_markdown"], "L'épreuve comporte deux parties indépendantes.")

    def test_preview_exposes_the_structured_choice_rules(self):
        regles = [{"type": "section_unique", "portee": "PAPER 3", "repondre": 4}]
        self.lesson.regles_choix = regles
        self.lesson.save(update_fields=["regles_choix"])

        self.assertEqual(self.client.get(f"/access/preview/{self.lesson.id}/").data["regles_choix"], regles)

    def test_preview_exposes_no_rule_when_every_question_is_compulsory(self):
        self.assertEqual(self.client.get(f"/access/preview/{self.lesson.id}/").data["regles_choix"], [])


class ReadCoursAPITests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.get(code="MATHS")
        self.cursus = Cursus.objects.get(examen=Examen.BAC, series__code="C")
        self.cours = Cours.objects.create(
            titre="Résolution d'équations", subject=self.subject, statut=StatutContenu.VALIDE,
            sections_raw=[
                {"type": "accroche", "contenu_markdown": "Accroche publique"},
                {"type": "exercices_application", "items": [
                    {"numero": 1, "difficulte": "facile", "enonce_markdown": "Exemple payant", "solution_markdown": "Solution payante"},
                ]},
            ],
        )
        self.cours.compile_from_sections()
        self.cours.cursus.add(self.cursus)
        self.user = User.objects.create_user(phone_number="677100003", password="x")
        self.profil = self.user.profils.first()
        self.client = APIClient()

    def test_read_cours_open_without_subscription_but_exercises_locked(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/access/cours/read/{self.cours.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Accroche publique", response.data["content_markdown"])
        self.assertNotIn("Exemple payant", response.data["content_markdown"])

    def test_read_cours_allowed_with_subscription_and_tracks_progress(self):
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f"/access/cours/read/{self.cours.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Exemple payant", response.data["content_markdown"])
        self.assertTrue(LectureProgress.objects.filter(profil=self.profil, cours=self.cours).exists())

    def test_preview_cours_never_exposes_paid_sections(self):
        response = self.client.get(f"/access/cours/preview/{self.cours.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Accroche publique", response.data["preview_markdown"])
        self.assertNotIn("Exemple payant", response.data["preview_markdown"])

    def test_read_cours_accepts_slug_as_well_as_numeric_id(self):
        # URL publique désormais /cours/<slug>/lire (voir l'audit UX) - l'id numérique
        # reste accepté en compat historique (voir Cours.save/par_slug_ou_id).
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f"/access/cours/read/{self.cours.slug}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], self.cours.titre)

    def test_preview_cours_accepts_slug_as_well_as_numeric_id(self):
        response = self.client.get(f"/access/cours/preview/{self.cours.slug}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Accroche publique", response.data["preview_markdown"])

    def test_read_cours_allowed_anonymously_and_never_tracks_progress(self):
        # Un cours est libre pour tous : un visiteur anonyme le lit (read_cours est AllowAny, comme read_lesson).
        # Jamais de suivi de lecture pour lui (pas de user à qui l'attacher) - voir `if request.user.is_authenticated`.
        response = self.client.get(f"/access/cours/read/{self.cours.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Accroche publique", response.data["content_markdown"])
        self.assertNotIn("Exemple payant", response.data["content_markdown"])
        self.assertFalse(LectureProgress.objects.filter(cours=self.cours).exists())

    def test_a_vitrine_source_does_not_unlock_the_exercises(self):
        vitrine_lesson = Lesson.objects.create(
            title="Maths BEPC vitrine", subject=self.subject, lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE, est_vitrine=True,
        )
        exercise = Exercise.objects.create(lesson=vitrine_lesson, numero_exercice="1", statut=StatutContenu.VALIDE)
        RappelDeMethode.objects.create(
            exercise=exercise, external_id="rdm-vitrine-anon", competence="Test",
            contenu_markdown="Contenu.", cours=self.cours,
        )

        response = self.client.get(f"/access/cours/read/{self.cours.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Exemple payant", response.data["content_markdown"])


class MyProgressionAPITests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.get(code="MATHS")
        self.cursus = Cursus.objects.get(examen=Examen.BAC, series__code="C")
        self.lesson = Lesson.objects.create(
            title="Maths BAC C 2024", subject=self.subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        self.lesson.cursus.add(self.cursus)
        self.user = User.objects.create_user(phone_number="677100004", password="x")
        self.profil = self.user.profils.first()
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
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

    def test_progression_filtered_to_cursus_prepare_when_declared(self):
        """Un compte avec deux abonnements actifs (voir le sélecteur d'examen) ne doit
        jamais voir les lectures de l'autre cursus une fois qu'il a basculé - c'est
        précisément le bug que ce filtre corrige."""
        autre_cursus = Cursus.objects.get(examen=Examen.BEPC)
        autre_lesson = Lesson.objects.create(
            title="Maths BEPC 2024", subject=self.subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        autre_lesson.cursus.add(autre_cursus)
        Subscription.objects.create(
            user=self.user, profil=self.profil, cursus=autre_cursus, expires_at=timezone.now() + timedelta(days=1),
        )
        self.client.get(f"/access/read/{self.lesson.id}/")
        self.client.get(f"/access/read/{autre_lesson.id}/")

        self.user.cursus_prepare = self.cursus
        self.user.save(update_fields=["cursus_prepare"])
        response = self.client.get("/access/progression/")
        self.assertEqual([l["id"] for l in response.data["lessons"]], [self.lesson.id])

        self.user.cursus_prepare = autre_cursus
        self.user.save(update_fields=["cursus_prepare"])
        response = self.client.get("/access/progression/")
        self.assertEqual([l["id"] for l in response.data["lessons"]], [autre_lesson.id])

    def test_progression_shows_cours_commun_a_toutes_les_series_regardless_of_cursus(self):
        """Un Cours sans cursus du tout (notion partagée, voir Cours.cursus) reste
        visible quel que soit le cursus actif - il n'est pas exclusif à l'un ou l'autre."""
        cours_commun = Cours.objects.create(
            subject=self.subject, titre="Notion commune", statut=StatutContenu.VALIDE,
        )
        LectureProgress.objects.create(profil=self.profil, cours=cours_commun)

        self.user.cursus_prepare = self.cursus
        self.user.save(update_fields=["cursus_prepare"])
        response = self.client.get("/access/progression/")
        self.assertEqual([c["id"] for c in response.data["cours"]], [cours_commun.id])


class AccesParProfilTests(TestCase):
    """Un abonnement est payé pour UN profil (Subscription.profil) : un frère ou une sœur du même
    compte, sans abonnement à son nom, ne doit jamais lire ce qui a été payé pour un autre."""

    def setUp(self):
        self.user = User.objects.create_user(phone_number="677100099", password="x")
        self.abonne = self.user.profils.first()
        self.sans_abonnement = Profil.objects.create(compte=self.user, prenom="Zaza", ordre=1)
        self.cursus = Cursus.objects.get(examen=Examen.BAC, series__code="C")
        self.lesson = Lesson.objects.create(
            title="Maths BAC C", subject=Subject.objects.get(code="MATHS"), lesson_type=LessonType.CORR,
            statut=StatutContenu.VALIDE, content_markdown="## Corrigé secret",
        )
        self.lesson.cursus.add(self.cursus)
        Subscription.objects.create(
            user=self.user, profil=self.abonne, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
        )
        InscriptionInedite.objects.create(
            user=self.user, profil=self.abonne, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=1),
        )

    def _client_du_profil(self, profil):
        token = AccessToken.for_user(self.user)
        token["profil_id"] = profil.id
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return client

    def test_has_access_suit_le_profil(self):
        self.assertTrue(has_access(self.user, self.lesson, self.abonne))
        self.assertFalse(has_access(self.user, self.lesson, self.sans_abonnement))

    def test_les_ensembles_de_cursus_suivent_le_profil(self):
        """Ensembles calculés une fois par requête (catalogue, recherche) : même règle que has_access."""
        self.assertEqual(bulk_active_subscription_cursus_ids(self.user, self.abonne), {self.cursus.id})
        self.assertEqual(bulk_active_subscription_cursus_ids(self.user, self.sans_abonnement), set())
        self.assertEqual(bulk_active_inedite_cursus_ids(self.user, self.abonne), {self.cursus.id})
        self.assertEqual(bulk_active_inedite_cursus_ids(self.user, self.sans_abonnement), set())

    def test_lecture_refusee_au_profil_sans_abonnement(self):
        reponse = self._client_du_profil(self.sans_abonnement).get(f"/access/read/{self.lesson.id}/")
        self.assertEqual(reponse.status_code, 403)
        self.assertNotIn("Corrigé secret", str(reponse.data))

    def test_lecture_autorisee_au_profil_abonne(self):
        reponse = self._client_du_profil(self.abonne).get(f"/access/read/{self.lesson.id}/")
        self.assertEqual(reponse.status_code, 200)
