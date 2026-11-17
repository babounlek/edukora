from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import AnalyticsEvent


class ViderAnalyticsAdminTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(phone_number="+237600000001", password="x-test-pass")
        self.client.force_login(self.admin)
        for i in range(3):
            AnalyticsEvent.objects.create(name=f"evt{i}", properties={})
        self.url = reverse("admin:analytics_analyticsevent_changelist")

    def test_sans_confirmation_rien_n_est_supprime(self):
        pk = AnalyticsEvent.objects.first().pk
        r = self.client.post(self.url, {"action": "vider_tout", "_selected_action": [pk]})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Oui, tout vider")
        self.assertEqual(AnalyticsEvent.objects.count(), 3)

    def test_avec_confirmation_toute_la_table_est_videe(self):
        pk = AnalyticsEvent.objects.first().pk
        self.client.post(self.url, {"action": "vider_tout", "vidage_confirme": "1", "_selected_action": [pk]})
        self.assertEqual(AnalyticsEvent.objects.count(), 0)
