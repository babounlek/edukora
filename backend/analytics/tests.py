"""
Couvre le seul risque réel de ce module : POST /analytics/events/ (voir
analytics.views.track_event) doit rester un vocabulaire fermé (EventName), jamais un
sink de texte libre arbitraire - voir la docstring d'AnalyticsEvent.
"""

from django.test import TestCase
from rest_framework.test import APIClient

from users.models import User

from .models import AnalyticsEvent, EventName


class TrackEventApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_records_a_known_event_anonymously(self):
        response = self.client.post("/analytics/events/", {"name": EventName.SEARCH_NO_RESULTS}, format="json")

        self.assertEqual(response.status_code, 201)
        event = AnalyticsEvent.objects.get()
        self.assertEqual(event.name, EventName.SEARCH_NO_RESULTS)
        self.assertIsNone(event.user)
        self.assertEqual(event.properties, {})

    def test_records_properties(self):
        response = self.client.post(
            "/analytics/events/",
            {"name": EventName.QUIZ_STARTED, "properties": {"cursus_id": 3}},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(AnalyticsEvent.objects.get().properties, {"cursus_id": 3})

    def test_associates_the_authenticated_user_when_present(self):
        user = User.objects.create_user(phone_number="677300001", password="x")
        self.client.force_authenticate(user=user)

        self.client.post("/analytics/events/", {"name": EventName.QUIZ_COMPLETED}, format="json")

        self.assertEqual(AnalyticsEvent.objects.get().user, user)

    def test_rejects_a_name_outside_the_closed_vocabulary(self):
        response = self.client.post("/analytics/events/", {"name": "n_importe_quoi"}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(AnalyticsEvent.objects.count(), 0)

    def test_rejects_a_missing_name(self):
        response = self.client.post("/analytics/events/", {}, format="json")

        self.assertEqual(response.status_code, 400)

    def test_rejects_properties_that_is_not_an_object(self):
        response = self.client.post(
            "/analytics/events/", {"name": EventName.SEARCH_NO_RESULTS, "properties": "pas un objet"}, format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(AnalyticsEvent.objects.count(), 0)

    def test_rejects_properties_with_too_many_keys(self):
        properties = {f"cle_{i}": i for i in range(11)}

        response = self.client.post(
            "/analytics/events/", {"name": EventName.SEARCH_NO_RESULTS, "properties": properties}, format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(AnalyticsEvent.objects.count(), 0)

    def test_records_inedit_tentative_events(self):
        # Épreuves Inédites (audit "Épreuves Inédites", phase KPI) - même mécanisme
        # générique que quiz_started/quiz_completed, rien de spécifique à ajouter ici.
        response = self.client.post(
            "/analytics/events/", {"name": EventName.INEDIT_TENTATIVE_STARTED}, format="json",
        )
        self.assertEqual(response.status_code, 201)

    def test_never_requires_authentication(self):
        # La majorité des évènements utiles (recherche sans résultat, abandon de
        # paiement avant connexion...) doivent pouvoir être enregistrés par un
        # visiteur anonyme.
        response = self.client.post("/analytics/events/", {"name": EventName.SEARCH_NO_RESULTS}, format="json")

        self.assertEqual(response.status_code, 201)
