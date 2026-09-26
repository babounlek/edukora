from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from catalog.models import Cours, Cursus, Examen, Lesson, LessonType, StatutContenu, Subject
from subscriptions.models import Subscription
from users.models import User

from .etude import MarqueInvalide, enregistrer_marque
from .models import MarqueEtude


class _Base(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="677500001", password="x")
        self.subject = Subject.objects.get(code="MATHS")
        self.cursus = Cursus.objects.get(examen=Examen.BAC, series__code="C")
        self.cours = Cours.objects.create(
            external_id="cours-etude", titre="Les limites", subject=self.subject, statut=StatutContenu.VALIDE,
        )
        self.cours.cursus.add(self.cursus)
        self.lesson = Lesson.objects.create(
            title="Maths BAC C 2024", subject=self.subject, lesson_type=LessonType.CORR, statut=StatutContenu.VALIDE,
        )
        self.lesson.cursus.add(self.cursus)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def _abonner(self, jours=5):
        Subscription.objects.create(
            user=self.user, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=jours),
        )


class EnregistrerMarqueTests(_Base):
    def test_a_partial_update_only_touches_the_given_fields(self):
        enregistrer_marque(self.user, self.cours, "regle", compris=True)
        enregistrer_marque(self.user, self.cours, "regle", note="Penser au cas limite")

        marque = MarqueEtude.objects.get(user=self.user, cours=self.cours, cle="regle")
        self.assertTrue(marque.compris)
        self.assertEqual(marque.note, "Penser au cas limite")

    def test_the_row_disappears_once_nothing_is_left(self):
        enregistrer_marque(self.user, self.cours, "regle", signet=True)

        resultat = enregistrer_marque(self.user, self.cours, "regle", signet=False)

        self.assertIsNone(resultat)
        self.assertFalse(MarqueEtude.objects.exists())

    def test_marks_on_a_lesson_and_a_course_do_not_collide(self):
        enregistrer_marque(self.user, self.cours, "exercice-1", signet=True)
        enregistrer_marque(self.user, self.lesson, "exercice-1", signet=True)

        self.assertEqual(MarqueEtude.objects.count(), 2)

    def test_a_malformed_key_is_rejected(self):
        for cle in ("", "Regle", "../etc", "a" * 61, "-x"):
            with self.assertRaises(MarqueInvalide):
                enregistrer_marque(self.user, self.cours, cle, signet=True)

    def test_an_oversized_note_is_rejected(self):
        with self.assertRaises(MarqueInvalide):
            enregistrer_marque(self.user, self.cours, "regle", note="x" * 2001)


class EtudeApiTests(_Base):
    def test_requires_authentication(self):
        response = APIClient().get("/access/etude/", {"cours": self.cours.slug})
        self.assertIn(response.status_code, (401, 403))

    def test_denied_without_access_to_the_document(self):
        response = self.client.put(
            "/access/etude/", {"cours": self.cours.slug, "cle": "regle", "signet": True}, format="json",
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(MarqueEtude.objects.exists())

    def test_400_without_a_target(self):
        self._abonner()
        self.assertEqual(self.client.get("/access/etude/").status_code, 400)

    def test_put_then_get_round_trip_on_a_course(self):
        self._abonner()

        put = self.client.put(
            "/access/etude/", {"cours": self.cours.slug, "cle": "regle", "compris": True, "note": "ok"}, format="json",
        )
        liste = self.client.get("/access/etude/", {"cours": self.cours.slug})

        self.assertEqual(put.status_code, 200)
        self.assertEqual([(m["cle"], m["compris"], m["note"]) for m in liste.data], [("regle", True, "ok")])

    def test_marks_are_private_to_their_owner(self):
        self._abonner()
        enregistrer_marque(self.user, self.cours, "regle", signet=True)
        autre = User.objects.create_user(phone_number="677500002", password="x")
        Subscription.objects.create(user=autre, cursus=self.cursus, expires_at=timezone.now() + timedelta(days=5))
        client = APIClient()
        client.force_authenticate(user=autre)

        self.assertEqual(client.get("/access/etude/", {"cours": self.cours.slug}).data, [])

    def test_invalid_key_returns_400(self):
        self._abonner()
        response = self.client.put(
            "/access/etude/", {"cours": self.cours.slug, "cle": "Pas Valide", "signet": True}, format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_carnet_lists_bookmarks_and_notes_but_not_bare_understood_flags(self):
        self._abonner()
        enregistrer_marque(self.user, self.cours, "regle", compris=True)
        enregistrer_marque(self.user, self.cours, "synthese", signet=True)
        enregistrer_marque(self.user, self.lesson, "exercice-2", note="Refaire")

        carnet = self.client.get("/access/etude/carnet/").data

        self.assertEqual({(m["type"], m["cle"]) for m in carnet}, {("cours", "synthese"), ("epreuve", "exercice-2")})
        cours = next(m for m in carnet if m["type"] == "cours")
        self.assertEqual(cours["slug"], self.cours.slug)
        self.assertEqual(cours["titre"], "Les limites")

    def test_carnet_keeps_the_notes_of_an_expired_subscription(self):
        enregistrer_marque(self.user, self.cours, "regle", note="Ma note")

        carnet = self.client.get("/access/etude/carnet/").data

        self.assertEqual(len(carnet), 1)
